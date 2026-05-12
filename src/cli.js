#!/usr/bin/env node
import { program } from 'commander';
import fs from 'fs';
import { validateInvoice } from './test-invoice.js';
import { generateInvoiceXML, saveXMLToFile } from './generators/xmlGenerator.js';
import QRCode from 'qrcode';

const sanitize = (t) => t ? String(t).replace(/[^a-zA-Z0-9 .,:@\/_-]/g, "?") : "N/A";

// === VALIDATE ===
program.command('validate')
  .requiredOption('-f, --file <path>')
  .action(opt => {
    try {
      const inv = JSON.parse(fs.readFileSync(opt.file,'utf8'));
      const r = validateInvoice(inv);
      console.log(r.isValid ? '✅ Valid' : '❌ '+JSON.stringify(r.errors));
    } catch(e){ console.error('❌',e.message); }
  });

// === GENERATE XML ===
program.command('generate')
  .requiredOption('-f, --file <path>')
  .requiredOption('-o, --output <path>')
  .action(opt => {
    try {
      const inv = JSON.parse(fs.readFileSync(opt.file,'utf8'));
      if(!validateInvoice(inv).isValid) return console.log('❌ Invalid');
      saveXMLToFile(generateInvoiceXML(inv), opt.output);
      console.log('✅ XML saved');
    } catch(e){ console.error('❌',e.message); }
  });

// === PREVIEW HTML ===
program.command('preview')
  .requiredOption('-f, --file <path>')
  .requiredOption('-o, --output <path>')
  .action(async opt => {
    try {
      const inv = JSON.parse(fs.readFileSync(opt.file,'utf8'));
      if(!validateInvoice(inv).isValid) return;
      const {generateInvoicePreview} = await import('./generators/htmlPreview.js');
      const {generateInvoiceXML, saveXMLToFile} = await import('./generators/xmlGenerator.js');
      const xml = generateInvoiceXML(inv); saveXMLToFile(xml,'samples/preview.xml');
      fs.writeFileSync(opt.output, generateInvoicePreview(inv,'samples/preview.xml'));
      console.log('✅ Preview saved');
    } catch(e){ console.error('❌',e.message); }
  });

// === PDF OFFICIAL (Detailed Table) ===
program.command('pdf')
  .requiredOption('-f, --file <path>')
  .requiredOption('-o, --output <path>')
  .option('--signed-xml <path>', 'Path to signed XML for QR hash')
  .action(async opt => {
    try {
      const inv = JSON.parse(fs.readFileSync(opt.file,'utf8'));
      if(!validateInvoice(inv).isValid) return console.log('❌ Invalid');
      const {PDFDocument, StandardFonts, rgb} = await import('pdf-lib');
      const doc = await PDFDocument.create();
      const page = doc.addPage([595,842]);
      const font = await doc.embedFont(StandardFonts.Helvetica);
      const bold = await doc.embedFont(StandardFonts.HelveticaBold);
      let y=810, m=40, pw=515;
      const black=rgb(0,0,0), blue=rgb(0,0.3,0.6), gray=rgb(0.5,0.5,0.5), lightGray=rgb(0.95,0.95,0.95);
      
      const drawLine = (x1,y1,x2,y2,c=black,w=0.5) => page.drawLine({start:{x:x1,y:y1},end:{x:x2,y:y2},color:c,thickness:w});
      const drawBox = (x,y,w,h,c=black,w2=0.5) => { drawLine(x,y,x+w,y,c,w2); drawLine(x,y-h,x+w,y-h,c,w2); drawLine(x,y,x,y-h,c,w2); drawLine(x+w,y,x+w,y-h,c,w2); };
      const fmt = (v) => (v||0).toFixed(3);
      
      // Header
      page.drawText('FACTURE ELECTRONIQUE', {x:m,y:y,size:18,font:bold,color:blue});
      page.drawText('TEIF v1.8 - Tunisia', {x:m,y:y-15,size:9,color:gray});
      y-=40;
      
      // Info Box
      drawBox(m,y+10,pw,50,black,1);
      page.drawText('No: '+sanitize(inv.invoiceNumber), {x:m+10,y:y-12,size:13,font:bold});
      page.drawText('Date: '+sanitize(inv.date), {x:m+10,y:y-28,size:10});
      y-=70;
      
      // Supplier/Customer with ICE
const colW = pw/2 - 10;
drawBox(m,y+10,colW,75,black,0.8);
page.drawText('SUPPLIER: '+sanitize(inv.supplier?.name), {x:m+10,y:y-15,size:9,font:bold});
page.drawText('VAT: '+sanitize(inv.supplier?.vatNumber), {x:m+10,y:y-30,size:8});
page.drawText('ICE: '+sanitize(inv.supplier?.ice), {x:m+10,y:y-42,size:7});
page.drawText('RC: '+sanitize(inv.supplier?.registrationNumber), {x:m+10,y:y-53,size:7});

drawBox(m+colW+20,y+10,colW,75,black,0.8);
page.drawText('CUSTOMER: '+sanitize(inv.customer?.name), {x:m+colW+30,y:y-15,size:9,font:bold});
page.drawText('VAT: '+sanitize(inv.customer?.vatNumber), {x:m+colW+30,y:y-30,size:8});
page.drawText('ICE: '+sanitize(inv.customer?.ice), {x:m+colW+30,y:y-42,size:7});
y-=90;

// Bank Details
const bank = inv.supplier?.bank;
if(bank && (bank.name || bank.iban || bank.rib)) {
  drawBox(m,y+10,pw,30,gray,0.5);
  page.drawText('BANK: '+sanitize(bank.name||''), {x:m+10,y:y-10,size:8,font:bold,color:gray});
  page.drawText('RIB: '+sanitize(bank.rib||''), {x:m+150,y:y-10,size:8,color:gray});
  page.drawText('IBAN: '+sanitize(bank.iban||''), {x:m+320,y:y-10,size:8,color:gray});
  y-=40;
} else {
  y-=10;
}
      
      // Table Header
      drawBox(m,y+10,pw,25,blue,1);
      page.drawText('ITEMS', {x:m+10,y:y-8,size:11,font:bold,color:blue});
      y-=30;
      const dW=150, uW=60, qW=40, tW=70, vW=40;
      const hY=y;
      page.drawRectangle({x:m,y:y-20,width:pw,height:20,color:lightGray,borderColor:black,borderWidth:0.5});
      page.drawText('Description', {x:m+5,y:y-15,size:9,font:bold});
      page.drawText('Unit HT', {x:m+dW+5,y:y-15,size:9,font:bold});
      page.drawText('Qty', {x:m+dW+uW+10,y:y-15,size:9,font:bold});
      page.drawText('Total HT', {x:m+dW+uW+qW+10,y:y-15,size:9,font:bold});
      page.drawText('VAT%', {x:m+dW+uW+qW+tW+10,y:y-15,size:9,font:bold});
      page.drawText('Total TTC', {x:m+dW+uW+qW+tW+vW+10,y:y-15,size:9,font:bold});
      y-=25;
      
      // Items
      const items = inv.items || [];
      const vatRate = inv.vatRate || 19;
      let totalHT = 0, totalVAT = 0, totalTTC = 0;
      
      items.forEach((it,idx) => {
        if(idx%2===1) page.drawRectangle({x:m,y:y-18,width:pw,height:18,color:rgb(0.98,0.98,0.98)});
        const desc = sanitize(it.name||it.description).slice(0,22);
        const qty = it.quantity||1;
        const uPrice = it.unitPrice||0;
        const htLine = qty*uPrice;
        const vatAmount = htLine*(vatRate/100);
        const ttcLine = htLine+vatAmount;
        totalHT += htLine; totalVAT += vatAmount; totalTTC += ttcLine;
        
        page.drawText(desc, {x:m+5,y:y-14,size:8,font});
        page.drawText(fmt(uPrice), {x:m+dW+10,y:y-14,size:8,font});
        page.drawText(String(qty), {x:m+dW+uW+15,y:y-14,size:8,font});
        page.drawText(fmt(htLine), {x:m+dW+uW+qW+10,y:y-14,size:8,font:bold});
        page.drawText(vatRate+'%', {x:m+dW+uW+qW+tW+10,y:y-14,size:8,font});
        page.drawText(fmt(ttcLine), {x:m+dW+uW+qW+tW+vW+10,y:y-14,size:8,font:bold});
        drawLine(m,y,m+pw,y,gray,0.3);
        y-=20;
      });
      
      // Table borders
      drawBox(m,hY+10,pw,(hY-y)+20,black,0.8);
      drawLine(m+dW,hY+10,m+dW,y,black,0.5);
      drawLine(m+dW+uW,hY+10,m+dW+uW,y,black,0.5);
      drawLine(m+dW+uW+qW,hY+10,m+dW+uW+qW,y,black,0.5);
      drawLine(m+dW+uW+qW+tW,hY+10,m+dW+uW+qW+tW,y,black,0.5);
      drawLine(m+dW+uW+qW+tW+vW,hY+10,m+dW+uW+qW+tW+vW,y,black,0.5);
      y-=20;
      
      // Totals
      const stamp = inv.stamp||0;
      const grandTotal = totalTTC + stamp;
      const tx = m+pw-200;
      drawBox(tx-10,y+10,200,85,blue,1);
      page.drawText('Subtotal HT:', {x:tx,y:y-12,size:10,font});
      page.drawText(fmt(totalHT)+' TND', {x:tx+90,y:y-12,size:10,font:bold});
      y-=18;
      page.drawText('VAT Amount:', {x:tx,y:y-12,size:10,font});
      page.drawText(fmt(totalVAT)+' TND', {x:tx+90,y:y-12,size:10,font:bold});
      y-=18;
      if(stamp>0) { page.drawText('Stamp:', {x:tx,y:y-12,size:10,font}); page.drawText(fmt(stamp)+' TND', {x:tx+90,y:y-12,size:10,font:bold}); y-=18; }
      page.drawRectangle({x:tx-5,y:y-22,width:190,height:20,color:blue});
      page.drawText('TOTAL TTC:', {x:tx+5,y:y-17,size:11,font:bold,color:rgb(1,1,1)});
      page.drawText(fmt(grandTotal)+' TND', {x:tx+85,y:y-17,size:11,font:bold,color:rgb(1,1,1)});
      y-=35;
      
      // QR Code
      const qrData = 'https://verify.elfatoora.tn/?inv='+inv.invoiceNumber;
      const qrImgData = await QRCode.toDataURL(qrData,{width:90,margin:0});
      const qrBuf = Buffer.from(qrImgData.split(',')[1],'base64');
      const qrImg = await doc.embedPng(qrBuf);
      page.drawImage(qrImg,{x:m,y:y-60,width:60,height:60});
      page.drawText('SCAN TO VERIFY', {x:m+70,y:y-20,size:9,font:bold,color:gray});
      page.drawText('verify.elfatoora.tn', {x:m+70,y:y-33,size:8,font});
      y-=70;
      
      // Footer
      drawLine(m,y+10,m+pw,y+10,black,0.5);
      y-=15;
      page.drawText('E-invoice per Tunisian Law 2000-17 | TEIF v1.8', {x:m,y:y,size:7,color:gray});
      page.drawText('Original XML is legal reference | Digitally signed', {x:m,y:y-10,size:7,color:gray});
      y-=25;
      drawBox(m+pw-120,y+10,120,50,black,0.8);
      page.drawText('Electronic Signature', {x:m+pw-110,y:y-10,size:8,font:bold,color:blue});
      page.drawText('[ TunTrust ]', {x:m+pw-100,y:y-25,size:7,color:gray});
      
      fs.writeFileSync(opt.output, await doc.save());
      console.log('✅ Official PDF saved: '+opt.output);
    } catch(e){ console.error('❌',e.message); }
  });
// === SIGN XML ===
program.command('sign')
  .requiredOption('-f, --file <path>', 'XML file to sign')
  .requiredOption('-c, --cert <path>', 'Certificate path (.crt / .pem)')
  .requiredOption('-k, --key <path>', 'Private key path (.key / .pem)')
  .requiredOption('-o, --output <path>', 'Output signed XML path')
  .action(async (opt) => {
    try {
      const { signInvoiceXML } = await import('./signers/xmlSigner.js');
      const signedXml = await signInvoiceXML(opt.file, opt.cert, opt.key);
      fs.writeFileSync(opt.output, signedXml);
      console.log('✅ XML signed (RSA-SHA256 + DSig + TLV QR):', opt.output);
    } catch(e) { console.error('❌ Error:', e.message); }
  });

// === SUBMIT TO TTN (El Fatoora) ===
program.command('submit')
  .requiredOption('-f, --file <path>', 'Signed XML file')
  .option('--client-id <id>', 'OAuth2 client ID')
  .option('--client-secret <secret>', 'OAuth2 client secret')
  .option('--tls-cert <path>', 'TUNTRUST TLS cert path (mTLS)')
  .option('--tls-key <path>', 'TUNTRUST TLS key path (mTLS)')
  .option('--api-key <key>', 'TTN API Key (legacy Basic Auth)')
  .option('--api-secret <secret>', 'TTN API Secret (legacy Basic Auth)')
  .option('--sandbox', 'Use sandbox environment', true)
  .action(async (opt) => {
    try {
      const { TTNClient } = await import('./api/ttnClient.js');

      if (opt.clientId && opt.clientSecret) {
        const client = new TTNClient({
          clientId: opt.clientId,
          clientSecret: opt.clientSecret,
          tlsCertPath: opt.tlsCert,
          tlsKeyPath: opt.tlsKey,
          sandbox: opt.sandbox
        });
        console.log('📤 Submitting to TTN (OAuth2)...');
        const result = await client.submitInvoice(opt.file);
        if (result.success) {
          console.log('✅ Submitted! UUID:', result.uuid);
          console.log('Status:', result.status);
        } else {
          console.error('❌ Failed:', result.error);
        }
      } else if (opt.apiKey && opt.apiSecret) {
        const { TTNClient: LegacyClient } = await import('./api/ttnClientLegacy.js');
        const client = new LegacyClient(opt.apiKey, opt.apiSecret, opt.sandbox);
        console.log('📤 Submitting to TTN (Basic Auth)...');
        const result = await client.submitInvoice(opt.file);
        if (result.success) {
          console.log('✅ Submitted! UUID:', result.uuid);
          console.log('Status:', result.status);
        } else {
          console.error('❌ Failed:', result.error);
        }
      } else {
        console.error('❌ Provide either --client-id/--client-secret (OAuth2) or --api-key/--api-secret (Basic Auth)');
      }
    } catch(e) { console.error('❌ Error:', e.message); }
  });

program.parse();
