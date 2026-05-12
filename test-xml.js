// Test XML generation workflow
import { validateInvoice } from './src/test-invoice.js';
import { generateInvoiceXML, saveXMLToFile } from './src/generators/xmlGenerator.js';

// Example Tunisian invoice data
const invoice = {
  invoiceNumber: "INV-2023-001",
  date: "2023-10-15",
  supplier: {
    name: "شركة التقنية المتطورة",
    vatNumber: "123456789012345",
    address: "تونس، الرياض، شارع الحرية 123"
  },
  customer: {
    name: "مؤسسة التسويق الرقمي",
    vatNumber: "987654321098765",
    address: "سليانة، شارع البحرين 45"
  },
  items: [
    {
      description: "تطوير تطبيق موبايل",
      quantity: 1,
      unitPrice: 5000,
      vatRate: 19,
      total: 5000
    },
    {
      description: "استشارات تقنية",
      quantity: 10,
      unitPrice: 200,
      vatRate: 19,
      total: 2000
    }
  ],
  totalAmount: 7000,
  vatAmount: 1330,
  totalWithVat: 8330
};

// Validate the invoice
const isValid = validateInvoice(invoice);
console.log('Invoice validation result:', isValid ? 'Valid' : 'Invalid');

if (isValid) {
  // Generate XML
  const xml = generateInvoiceXML(invoice);
  
  // Save to file
  const filePath = 'samples/test-invoice.xml';
  saveXMLToFile(xml, filePath);
  
  console.log('XML saved to:', filePath);
} else {
  console.log('Cannot generate XML for invalid invoice');
}
