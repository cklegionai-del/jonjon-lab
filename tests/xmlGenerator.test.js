// Test file for XML Generator
import { generateInvoiceXML, saveXMLToFile } from '../src/generators/xmlGenerator.js';

// Mock invoice data
const mockInvoice = {
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

// Test the XML generation
describe('XML Generator', () => {
  test('should generate valid XML structure', () => {
    const xml = generateInvoiceXML(mockInvoice);
    
    // Check that all required elements are present
    expect(xml).toContain('<ID>INV-2023-001</ID>');
    expect(xml).toContain('<IssueDate>2023-10-15</IssueDate>');
    expect(xml).toContain('<DocumentCurrencyCode>TND</DocumentCurrencyCode>');
    expect(xml).toContain('<Name>شركة التقنية المتطورة</Name>');
    expect(xml).toContain('<ID schemeID="TN_MF">123456789012345</ID>');
    expect(xml).toContain('<StreetName>تونس، الرياض، شارع الحرية 123</StreetName>');
    expect(xml).toContain('<Name>تطوير تطبيق موبايل</Name>');
    expect(xml).toContain('<InvoicedQuantity unitCode="HUR">1.000</InvoicedQuantity>');
    expect(xml).toContain('<PriceAmount currencyID="TND">5000.000</PriceAmount>');
    expect(xml).toContain('<Percent>19</Percent>');
    expect(xml).toContain('<LineExtensionAmount currencyID="TND">5000.000</LineExtensionAmount>');
    expect(xml).toContain('<LineExtensionAmount currencyID="TND">7000.000</LineExtensionAmount>');
    expect(xml).toContain('<TaxAmount currencyID="TND">1330.000</TaxAmount>');
    expect(xml).toContain('<PayableAmount currencyID="TND">8330.000</PayableAmount>');
    
    // Check that it's valid XML (basic check)
    expect(xml).toMatch(/^<\?xml/);
    expect(xml).toContain('</Invoice>');
  });

  test('should format numbers correctly', () => {
    const xml = generateInvoiceXML(mockInvoice);
    
    // Check that numbers are formatted with 3 decimal places
    expect(xml).toContain('<InvoicedQuantity unitCode="HUR">1.000</InvoicedQuantity>');
    expect(xml).toContain('<PriceAmount currencyID="TND">5000.000</PriceAmount>');
    expect(xml).toContain('<Percent>19</Percent>');
    expect(xml).toContain('<LineExtensionAmount currencyID="TND">5000.000</LineExtensionAmount>');
    expect(xml).toContain('<LineExtensionAmount currencyID="TND">7000.000</LineExtensionAmount>');
    expect(xml).toContain('<TaxAmount currencyID="TND">1330.000</TaxAmount>');
    expect(xml).toContain('<PayableAmount currencyID="TND">8330.000</PayableAmount>');
  });

  test('should handle saveXMLToFile function', () => {
    const xml = generateInvoiceXML(mockInvoice);
    const result = saveXMLToFile(xml, 'samples/test-invoice.xml');
    
    // Mock function should return true
    expect(result).toBe(true);
  });
});
