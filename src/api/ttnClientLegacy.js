import axios from 'axios';
import fs from 'fs';

const TTN_SANDBOX = 'https://api-sandbox.elfatoora.tn/api/v1';
const TTN_PROD = 'https://api.elfatoora.tn/api/v1';

// Legacy Basic Auth — used as fallback when OAuth2 is not available
export class TTNClient {
  constructor(apiKey, apiSecret, sandbox = true) {
    this.client = axios.create({
      baseURL: sandbox ? TTN_SANDBOX : TTN_PROD,
      headers: {
        'Content-Type': 'application/xml',
        'Accept': 'application/json'
      },
      auth: { username: apiKey, password: apiSecret }
    });
  }

  async submitInvoice(signedXmlPath) {
    const xml = fs.readFileSync(signedXmlPath, 'utf8');
    try {
      const res = await this.client.post('/invoices', xml);
      return { success: true, uuid: res.data.uuid, status: res.data.status };
    } catch (err) {
      return { success: false, error: err.response?.data || err.message };
    }
  }

  async checkStatus(uuid) {
    try {
      const res = await this.client.get('/invoices/' + uuid);
      return res.data;
    } catch (err) {
      return { error: err.message };
    }
  }
}
