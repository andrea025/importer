<template>
  <div>
    <div class="row">
      <div class="col-md-10 offset-md-1">
        <div class="card">
          <div class="card-header">
            <h4>Import Adversary Emulation Plan</h4>
          </div>
          <div class="card-body">
            <div class="alert alert-info" role="alert">
              <p>Upload a YAML file containing an adversary emulation plan to automatically create adversaries and abilities in CALDERA.</p>
              <p>The YAML file should follow the structure shown in the example below.</p>
            </div>

            <form @submit.prevent="uploadEmulationPlan" enctype="multipart/form-data">
              <div class="form-group">
                <label for="emulation_plan_file">Select Emulation Plan YAML File</label>
                <input type="file" class="form-control-file" id="emulation_plan_file" 
                       ref="fileInput" accept=".yaml,.yml" required>
              </div>
              <button type="submit" class="btn btn-primary mt-2" :disabled="isUploading">
                <span v-if="isUploading" class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
                {{ isUploading ? 'Importing...' : 'Import' }}
              </button>
            </form>
            
            <div v-if="showResult" class="mt-3">
              <div :class="['alert', resultStatus === 'success' ? 'alert-success' : 'alert-danger']">
                {{ resultMessage }}
              </div>
              <div v-if="resultStatus === 'success' && resultDetails" class="card mt-3">
                <div class="card-header">
                  <h5>Import Details</h5>
                </div>
                <div class="card-body">
                  <table class="table table-sm">
                    <tbody>
                      <tr>
                        <th scope="row">Adversary ID:</th>
                        <td>{{ resultDetails.adversary_id }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Adversary Name:</th>
                        <td>{{ resultDetails.adversary_name }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Abilities Count:</th>
                        <td>{{ resultDetails.abilities_count }}</td>
                      </tr>
                      <tr>
                        <th scope="row">Processing Time:</th>
                        <td>{{ resultDetails.processing_time }}</td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="mt-3">
                    <router-link to="/campaigns/agents" class="btn btn-primary">View in Adversaries</router-link>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-4">
              <h5>Example YAML Structure</h5>
              <pre class="p-3 bg-light"><code>
- emulation_plan_details:
    id: 186b4d47-f4c0-48cb-9688-887070db45f1
    adversary_name: Carbanak
    adversary_description: An advanced attacker targeting financial institutions
    attack_version: 8.1
    format_version: 1.0

- id: 453cb643-892b-475d-8db9-df61289749f1
  name: Screen Capture
  description: Download screen capture PowerShell script to target and execute
  tactic: collection
  technique:
    attack_id: T1113
    name: "Screen Capture"
  platforms:
    windows:
      psh,pwsh:
        command: |
          powershell.exe -ExecutionPolicy Bypass -File .\take-screenshot.ps1
        payloads:
        - take-screenshot.ps1
        cleanup: |
          Remove-Item -Force screenshot__.png
              </code></pre>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'Importer',
  data() {
    return {
      isUploading: false,
      showResult: false,
      resultStatus: '',
      resultMessage: '',
      resultDetails: null
    };
  },
  methods: {
    async uploadEmulationPlan() {
      // Reset result display
      this.showResult = false;
      
      // Get file
      const fileInput = this.$refs.fileInput;
      if (!fileInput.files.length) {
        this.showResultMessage('error', 'Please select a file to upload.');
        return;
      }
      
      // Create form data
      const formData = new FormData();
      formData.append('emulation_plan_file', fileInput.files[0]);
      
      // Set loading state
      this.isUploading = true;
      
      try {
        // Make API request
        const response = await this.$http.post('/plugin/importer/upload', formData);
        const data = response.data;
        
        if (data.status === 'success') {
          this.showResultMessage('success', data.message, data.details);
        } else {
          this.showResultMessage('error', data.message);
        }
      } catch (error) {
        this.showResultMessage('error', `Error uploading emulation plan: ${error.message || 'Unknown error'}`);
      } finally {
        this.isUploading = false;
      }
    },
    
    showResultMessage(status, message, details = null) {
      this.resultStatus = status;
      this.resultMessage = message;
      this.resultDetails = details;
      this.showResult = true;
    }
  }
};
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 0.85rem;
}
</style>
