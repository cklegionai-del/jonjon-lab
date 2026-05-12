import axios from 'axios';
import fs from 'fs';
import https from 'https';

const TTN_SANDBOX = 'https://api-sandbox.elfatoora.tn/api/v1';
const TTN_PROD = 'https://api.elfatoora.tn/api/v1';
const AUTH_SANDBOX = 'https://api-sandbox.elfatoora.tn/auth/realms/ttn/protocol/openid-connect/token';
const AUTH_PROD = 'https://api.elfatoora.tn/auth/realms/ttn/protocol/openid-connect/token';

export class TTNClient {
  constructor({ clientId, clientSecret, tlsCertPath, tlsKeyPath, sandbox = true }) {
    this.clientId = clientId;
    this.clientSecret = clientSecret;
    this.sandbox = sandbox;

    this.baseURL = sandbox ? TTN_SANDBOX : TTN_PROD;
    this.authURL = sandbox ? AUTH_SANDBOX : AUTH_PROD;

    // Build mTLS agent if cert paths provided
    let httpsAgent = undefined;
    if (tlsCertPath && tlsKeyPath) {
      const cert = fs.readFileSync(tlsCertPath);
      const key = fs.readFileSync(tlsKeyPath);
      httpsAgent = new https.Agent({ cert, key });
    }

    this.apiClient = axios.create({
      baseURL: this.baseURL,
      headers: {
        'Accept': 'application/json'
      },
      httpsAgent
    });

    this.token = null;
    this.tokenExpiry = 0;
  }

  async getAccessToken() {
    if (this.token && Date.now() < this.tokenExpiry) {
      return this.token;
    }

    const params = new URLSearchParams();
    params.append('grant_type', 'client_credentials');
    params.append('client_id', this.clientId);
    params.append('client_secret', this.clientSecret);

    try {
      const res = await axios.post(this.authURL, params.toString(), {
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' }
      });

      this.token = res.data.access_token;
      this.tokenExpiry = Date.now() + (res.data.expires_in - 60) * 1000; // 60s buffer
      return this.token;
    } catch (err) {
      throw new Error('OAuth2 token failed: ' + (err.response?.data?.error_description || err.message));
    }
  }

  async submitInvoice(signedXmlPath) {
    const xml = fs.readFileSync(signedXmlPath, 'utf8');
    const token = await this.getAccessToken();

    try {
      const res = await this.apiClient.post('/invoices', xml, {
        headers: {
          'Content-Type': 'application/xml',
          'Authorization': 'Bearer ' + token
        }
      });
      return { success: true, uuid: res.data.uuid, status: res.data.status };
    } catch (err) {
      if (err.response?.status === 401) {
        this.token = null;
      }
      return { success: false, error: err.response?.data || err.message };
    }
  }

  async checkStatus(uuid) {
    const token = await this.getAccessToken();

    try {
      const res = await this.apiClient.get('/invoices/' + uuid, {
        headers: { 'Authorization': 'Bearer ' + token }
      });
      return res.data;
    } catch (err) {
      if (err.response?.status === 401) {
        this.token = null;
      }
      return { error: err.message };
    }
  }
}
