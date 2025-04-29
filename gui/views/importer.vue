<template>
  <div>
    <div class="row">
      <div class="col-md-10 offset-md-1">
        <div class="card shadow-sm mb-4">
          <div class="card-header bg-primary text-white">
            <h3 class="mb-0"><i class="material-icons align-middle mr-2">upload_file</i> Adversary Emulation Plan Importer</h3>
          </div>
          <div class="card-body">
            <div class="alert alert-info shadow-sm" role="alert">
              <h5 class="alert-heading"><i class="material-icons align-middle mr-1" style="font-size: 1.2rem;">info</i> About This Tool</h5>
              <p>This tool allows you to import YAML-formatted adversary emulation plans directly into CALDERA, automatically creating adversary profiles and abilities for red team operations.</p>
              <hr>
              <p class="mb-0">Simply upload your YAML file, and the importer will handle the rest.</p>
            </div>

            <div class="card shadow-sm mb-4">
              <div class="card-header bg-light">
                <h4 class="mb-0">Upload Emulation Plan</h4>
              </div>
              <div class="card-body">
                <form @submit.prevent="uploadEmulationPlan" enctype="multipart/form-data">
                  <div class="form-group">
                    <label for="emulation_plan_file" class="font-weight-bold">Select Emulation Plan YAML File</label>
                    <div class="custom-file">
                      <input type="file" class="custom-file-input" id="emulation_plan_file" 
                            ref="fileInput" accept=".yaml,.yml" required>
                      <label class="custom-file-label" for="emulation_plan_file">Choose file...</label>
                    </div>
                    <small class="form-text text-muted">Accepted file types: .yaml, .yml</small>
                  </div>
                  <button type="submit" class="btn btn-primary mt-3 px-4" :disabled="isUploading">
                    <i class="material-icons align-middle mr-1" style="font-size: 1.2rem;">cloud_upload</i>
                    <span v-if="isUploading" class="spinner-border spinner-border-sm mr-1" role="status" aria-hidden="true"></span>
                    {{ isUploading ? 'Importing...' : 'Import Emulation Plan' }}
                  </button>
                </form>
              </div>
            </div>
            
            <div v-if="showResult" class="mb-4">
              <div :class="['alert', 'shadow-sm', resultStatus === 'success' ? 'alert-success' : 'alert-danger']">
                <h5 class="alert-heading">
                  <i :class="['material-icons', 'align-middle', 'mr-1']" style="font-size: 1.2rem;">
                    {{ resultStatus === 'success' ? 'check_circle' : 'error' }}
                  </i>
                  {{ resultStatus === 'success' ? 'Success!' : 'Error' }}
                </h5>
                <p>{{ resultMessage }}</p>
              </div>
              <div v-if="resultStatus === 'success' && resultDetails" class="card shadow-sm">
                <div class="card-header bg-success text-white">
                  <h5 class="mb-0"><i class="material-icons align-middle mr-1">assignment_turned_in</i> Import Details</h5>
                </div>
                <div class="card-body">
                  <table class="table table-bordered table-sm">
                    <tbody>
                      <tr>
                        <th scope="row" class="bg-light" style="width: 25%">Adversary ID:</th>
                        <td><code>{{ resultDetails.adversary_id }}</code></td>
                      </tr>
                      <tr>
                        <th scope="row" class="bg-light">Adversary Name:</th>
                        <td><strong>{{ resultDetails.adversary_name }}</strong></td>
                      </tr>
                      <tr>
                        <th scope="row" class="bg-light">Abilities Count:</th>
                        <td>{{ resultDetails.abilities_count }}</td>
                      </tr>
                      <tr>
                        <th scope="row" class="bg-light">Processing Time:</th>
                        <td>{{ resultDetails.processing_time }}</td>
                      </tr>
                    </tbody>
                  </table>
                  <div class="mt-3">
                    <router-link to="/campaigns/agents" class="btn btn-success">
                      <i class="material-icons align-middle mr-1">visibility</i> View in Adversaries
                    </router-link>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="card shadow-sm">
              <div class="card-header bg-light">
                <h4 class="mb-0">Example YAML Format</h4>
              </div>
              <div class="card-body">
                <pre class="p-3 bg-light border rounded"><code>
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
      resultDetails: null,
      fileName: 'Choose file...'
    };
  },
  mounted() {
    // Update file input label with selected filename
    this.$nextTick(() => {
      const fileInput = this.$refs.fileInput;
      if (fileInput) {
        fileInput.addEventListener('change', (e) => {
          if (e.target.files.length > 0) {
            // Update label with file name
            const label = document.querySelector('.custom-file-label');
            if (label) {
              label.textContent = e.target.files[0].name;
            }
          }
        });
      }
    });
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
      
      // Scroll to result
      this.$nextTick(() => {
        const resultElement = document.querySelector('.alert');
        if (resultElement) {
          resultElement.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }
      });
    }
  }
};
</script>

<style scoped>
pre {
  white-space: pre-wrap;
  word-wrap: break-word;
  font-size: 0.85rem;
  max-height: 350px;
  overflow-y: auto;
}

.card {
  border-radius: 0.25rem;
}

.card-header {
  font-weight: 500;
}

.material-icons {
  vertical-align: middle;
}

.alert {
  border: none;
}

.table th {
  width: 30%;
}

code {
  background-color: rgba(0, 0, 0, 0.05);
  padding: 0.2rem 0.4rem;
  border-radius: 0.2rem;
}
</style>
