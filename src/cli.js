#!/usr/bin/env node
import { program } from 'commander';
import fs from 'fs';
import { validateInvoice } from '../test-invoice.js';
import { generateInvoiceXML, saveXMLToFile } from './generators/xmlGenerator.js';

// Helper: Sanitize text for PDF (remove non-ASCII to avoid WinAnsi error)
const sanitizeForPDF = (text) => {
  if (!text) return 'N/A';
  return String(text).replace(/[^\x20-\x7E]/g, '?'); // Replace Arabic/special chars with ?
};

// Validate command
program
  .command('validate')
  .description('Validate invoice JSON')
  .requiredOption('-f, --file <path>', 'Path to invoice JSON')
  .action((options) => {
    try {
      const invoice = JSON.parse(fs.readFileSync(options.file, 'utf8'));
      const result = validateInvoice(invoice);
      if (result.isValid) { console.log('✅ Invoice valid'); }
      else { console.log('❌ Errors:', result.errors); process.exit(1); }
    } catch (err) { console.error('❌ Error:', err.message); process.exit(1); }
  });

// Generate command
program
  .command('generate')
  .description('Generate TEIF XML invoice')
  .requiredOption('-f, --file <path>', 'Path to invoice JSON')
  .requiredOption('-o, --output <path>', 'Output XML path')
  .action((options) => {
    try {
      const invoice = JSON.parse(fs.readFileSync(options.file, 'utf8'));
      const result = validateInvoice(invoice);
      if (!result.isValid) { console.log('❌ Cannot generate XML for invalid invoice'); process.exit(1); }
      const xml = generateInvoiceXML(invoice);
      saveXMLToFile(xml, options.output);
    } catch (err) { console.error('❌ Error:', err.message); process.exit(1); }
  });

// Preview command
program
  .command('preview')
  .description('Generate HTML preview')
  .requiredOption('-f, --file <path>', 'Path to invoice JSON')
  .requiredOption('-o, --output <path>', 'Output HTML path')
  .action(async (options) => {
    try {
      const invoice = JSON.parse(fs.readFileSync(options.file, 'utf8'));
      const { validateInvoice } = await import('../test-invoice.js');
      const result = validateInvoice(invoice);
      if (!result.isValid) { console.error('❌ Errors:', result.errors); return; }
      console.log('✅ Invoice valid');
      const { generateInvoiceXML, saveXMLToFile } = await import('./generators/xmlGenerator.js');
      const xml = generateInvoiceXML(invoice);
      const xmlPath = 'samples/preview.xml';
      saveXMLToFile(xml, xmlPath);
      const { generateInvoicePreview } = await import('./generators/htmlPreview.js');
      const html = generateInvoicePreview(invoice, xmlPath);
      saveXMLToFile(html, options.output);
      console.log(`✅ Preview saved: ${options.output}`);
    } catch (err) { console.error('❌ Error:', err.message); }
  });

// PDF command (MVP: Sanitized Latin-only output)
program
  .command('pdf')
  .description('Generate PDF invoice (MVP)')
  .requiredOption('-f, --file <path>', 'Path to invoice JSON')
  .requiredOption('-o, --output <path>', 'Output PDF path')
  .action(async (options) => {
    try {
      const invoice = JSON.parse(fs.readFileSync(options.file, 'utf8'));
      const { validateInvoice } = await import('../test-invoice.js');
      const result = validateInvoice(invoice);
      if (!result.isValid) { console.error('❌ Errors:', result.errors); return; }
      console.log('✅ Invoice valid');

      const { PDFDocument, StandardFonts, rgb } = await import('pdf-lib');
      const pdfDoc = await PDFDocument.create();
      const page = pdfDoc.addPage([595, 842]);
      const font = await pdfDoc.embedFont(StandardFonts.Helvetica);
      
      // Use sanitizeForPDF() on ALL dynamic text from invoice
      page.drawText('INVOICE', { x: 50, y: 800, size: 20, font });
      page.drawText('Number: ' + sanitizeForPDF(invoice.invoiceNumber), { x: 50, y: 760, size: 12, font });
      page.drawText('Date: ' + sanitizeForPDF(invoice.date), { x: 50, y: 740, size: 12, font });
      page.drawText('Supplier: ' + sanitizeForPDF(invoice.supplier?.name), { x: 50, y: 720, size: 12, font });
      page.drawText('Customer: ' + sanitizeForPDF(invoice.customer?.name), { x: 50, y: 700, size: 12, font });
      page.drawText('Total: ' + (invoice.totalWithVat?.toFixed(3) || '0.000') + ' TND', { x: 50, y: 670, size: 14, font, color: rgb(0, 0.4, 0.8) });
      page.drawText('Preview - Testing Only', { x: 50, y: 50, size: 10, font, color: rgb(0.5, 0.5, 0.5) });

      const pdfBytes = await pdfDoc.save();
      fs.writeFileSync(options.output, pdfBytes);
      console.log(`✅ PDF saved: ${options.output}`);
    } catch (err) { console.error('❌ Error:', err.message); }
  });

program.parse();
