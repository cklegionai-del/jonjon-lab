#!/usr/bin/env node

import { program } from 'commander';
import fs from 'fs';
import path from 'path';
import { validateInvoice } from '../test-invoice.js';
import { generateInvoiceXML, saveXMLToFile } from './generators/xmlGenerator.js';

// Read and parse JSON file
function readInvoiceFile(filePath) {
  try {
    const data = fs.readFileSync(filePath, 'utf8');
    return JSON.parse(data);
  } catch (error) {
    console.error('❌ Error reading file:', error.message);
    process.exit(1);
  }
}

// Validate command
program
  .command('validate')
  .description('Validate an invoice file')
  .option('-f, --file <path>', 'Path to the invoice JSON file')
  .action((options) => {
    if (!options.file) {
      console.error('❌ Please provide a file path with --file option');
      process.exit(1);
    }

    const invoice = readInvoiceFile(options.file);
    const isValid = validateInvoice(invoice);

    if (isValid) {
      console.log('✅ فاتورة صحيحة');
    } else {
      console.log('❌ أخطاء في الفاتورة');
      // In a real implementation, you would provide more detailed validation errors
    }
  });

// Generate command
program
  .command('generate')
  .description('Generate XML from an invoice file')
  .option('-f, --file <path>', 'Path to the invoice JSON file')
  .option('-o, --output <path>', 'Output XML file path')
  .action((options) => {
    if (!options.file) {
      console.error('❌ Please provide a file path with --file option');
      process.exit(1);
    }

    if (!options.output) {
      console.error('❌ Please provide an output path with --output option');
      process.exit(1);
    }

    const invoice = readInvoiceFile(options.file);
    const isValid = validateInvoice(invoice);

    if (!isValid) {
      console.log('❌ Cannot generate XML for invalid invoice');
      process.exit(1);
    }

    const xml = generateInvoiceXML(invoice);
    saveXMLToFile(xml, options.output);
  });

// === NEW: Preview Command ===
program
  .command('preview')
  .description('عرض معاينة HTML للفاتورة')
  .requiredOption('-f, --file <path>', 'مسار ملف الفاتورة JSON')
  .requiredOption('-o, --output <path>', 'مسار حفظ ملف HTML')
  .action(async (options) => {
    try {
      const invoice = JSON.parse(fs.readFileSync(options.file, 'utf8'));
      const { validateInvoice } = await import('../test-invoice.js');
      const result = validateInvoice(invoice);

      if (!result.isValid) {
        console.error('❌ أخطاء في الفاتورة:', result.errors);
        return;
      }
      console.log('✅ فاتورة صحيحة');

      const { generateInvoiceXML, saveXMLToFile } = await import('./generators/xmlGenerator.js');
      const xml = generateInvoiceXML(invoice);
      const xmlPath = 'samples/preview.xml';
      saveXMLToFile(xml, xmlPath);

      const { generateInvoicePreview } = await import('./generators/htmlPreview.js');
      const html = generateInvoicePreview(invoice, xmlPath);
      saveXMLToFile(html, options.output);

      console.log(`✅ Preview saved to: ${options.output}`);
      console.log(`📄 XML: ${xmlPath}`);
    } catch (err) {
      console.error('❌ Error:', err.message);
    }
  });

program.parse();
