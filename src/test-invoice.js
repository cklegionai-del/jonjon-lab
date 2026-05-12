// Mock invoice validator
export function validateInvoice(invoice) {
  const errors = [];
  const warnings = [];

  // Validate basic fields
  if (!invoice.invoiceNumber || typeof invoice.invoiceNumber !== 'string') {
    errors.push('invoiceNumber is required and must be a string');
  }

  if (!invoice.date || typeof invoice.date !== 'string') {
    errors.push('date is required and must be a string');
  }

  // Validate supplier
  if (!invoice.supplier) {
    errors.push('supplier is required');
  } else {
    if (!invoice.supplier.name || typeof invoice.supplier.name !== 'string') {
      errors.push('supplier.name is required and must be a string');
    }
    
    if (!invoice.supplier.vatNumber || typeof invoice.supplier.vatNumber !== 'string') {
      errors.push('supplier.vatNumber is required and must be a string');
    }
    
    if (!invoice.supplier.address || typeof invoice.supplier.address !== 'string') {
      errors.push('supplier.address is required and must be a string');
    }
  }

  // Validate customer
  if (!invoice.customer) {
    errors.push('customer is required');
  } else {
    if (!invoice.customer.name || typeof invoice.customer.name !== 'string') {
      errors.push('customer.name is required and must be a string');
    }
    
    if (!invoice.customer.vatNumber || typeof invoice.customer.vatNumber !== 'string') {
      errors.push('customer.vatNumber is required and must be a string');
    }
    
    if (!invoice.customer.address || typeof invoice.customer.address !== 'string') {
      errors.push('customer.address is required and must be a string');
    }
  }

  // Validate items
  if (!invoice.items || !Array.isArray(invoice.items)) {
    errors.push('items is required and must be an array');
  } else {
    invoice.items.forEach((item, index) => {
      if (!item.description || typeof item.description !== 'string') {
        errors.push(`items[${index}].description is required and must be a string`);
      }
      
      if (typeof item.quantity !== 'number' || item.quantity < 0) {
        errors.push(`items[${index}].quantity must be a non-negative number`);
      }
      
      if (typeof item.unitPrice !== 'number' || item.unitPrice < 0) {
        errors.push(`items[${index}].unitPrice must be a non-negative number`);
      }
      
      if (typeof item.vatRate !== 'number' || item.vatRate < 0) {
        errors.push(`items[${index}].vatRate must be a non-negative number`);
      }
      
      if (typeof item.total !== 'number' || item.total < 0) {
        errors.push(`items[${index}].total must be a non-negative number`);
      }
    });
  }

  // Validate totals
  if (typeof invoice.totalAmount !== 'number' || invoice.totalAmount < 0) {
    errors.push('totalAmount must be a non-negative number');
  }
  
  if (typeof invoice.vatAmount !== 'number' || invoice.vatAmount < 0) {
    errors.push('vatAmount must be a non-negative number');
  }
  
  if (typeof invoice.totalWithVat !== 'number' || invoice.totalWithVat < 0) {
    errors.push('totalWithVat must be a non-negative number');
  }

  // Validate VAT numbers format (15 digits)
  if (invoice.supplier.vatNumber && invoice.supplier.vatNumber.length !== 15) {
    warnings.push('supplier.vatNumber should be 15 digits');
  }
  
  if (invoice.customer.vatNumber && invoice.customer.vatNumber.length !== 15) {
    warnings.push('customer.vatNumber should be 15 digits');
  }

  // Validate date format (YYYY-MM-DD)
  const dateRegex = /^\d{4}-\d{2}-\d{2}$/;
  if (invoice.date && !dateRegex.test(invoice.date)) {
    errors.push('date must be in YYYY-MM-DD format');
  }

  // Validate amounts consistency
  if (invoice.items && invoice.items.length > 0) {
    const calculatedTotal = invoice.items.reduce((sum, item) => sum + item.total, 0);
    if (Math.abs(calculatedTotal - invoice.totalAmount) > 0.01) {
      errors.push('totalAmount does not match sum of item totals');
    }
  }

  return {
    isValid: errors.length === 0,
    errors,
    warnings
  };
}

// Test code for direct execution
if (process.argv[1] === new URL(import.meta.url).pathname) {
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
  const result = validateInvoice(invoice);
  console.log('Invoice validation result:', result.isValid ? 'Valid' : 'Invalid');
  if (result.errors.length > 0) {
    console.log('Errors:', result.errors);
  }
  if (result.warnings.length > 0) {
    console.log('Warnings:', result.warnings);
  }
  console.log('Invoice data:', invoice);
}
