import { sendMessage,AddBase } from './public_usage.js';

const baseAssetPath = '../../asset/';

const setAPIKeyButton = document.getElementById('SetAPIKeyButton');
const apiKeyInput = document.getElementById('apiKeyInput');
const BaseSelect = document.getElementById('BaseSelect');
const ModelSelect = document.getElementById('ModelSelect');
const agentImage = document.getElementById('agentImage');

let option=null;

async function optionReader(){
    if (option != null)return option;
    else{
        const response = await fetch(AddBase("get_agent_provider"));
        const data = await response.json();
        option = data.provider;
        if (option != null) return option;
        else return null;
    }
}
setAPIKeyButton.addEventListener('click', () => {
    setAPIKeyButton.hidden = !setAPIKeyButton.hidden;
    BaseSelect.hidden = !BaseSelect.hidden;
});
const BaseObserver = new MutationObserver(async ()=>{
    if(!BaseSelect.hidden){
        const response = await fetch(AddBase("get_base_list"));

        const data = await response.json();
        const list = data.bases;

        BaseSelect.innerHTML = ''; // Clear existing options
        const default_op = document.createElement('option');
        default_op.value = 'Please select a Provider';
        default_op.textContent = 'Please select a Provider';
        default_op.disabled = true;
        default_op.selected = true;
        BaseSelect.appendChild(default_op);

        list.forEach(base => {
            const option = document.createElement('option');
            option.value = base;
            option.textContent = base;
            BaseSelect.appendChild(option);
        });
    }
});
BaseObserver.observe(BaseSelect, { attributes: true, attributeFilter: ['hidden'] });

BaseSelect.addEventListener('change', () => {
    BaseSelect.hidden = !BaseSelect.hidden;
    apiKeyInput.hidden = !apiKeyInput.hidden;
    option = BaseSelect.value;

    const address=baseAssetPath + option + '.jpeg';
    agentImage.src = address;
    console.log('Selected new address:', address);
});
apiKeyInput.addEventListener('keydown', async (e) => {
    if(e.key === 'Enter') {
        const apiKey = String(option) + ' ' + apiKeyInput.value;
        sendMessage(apiKey,AddBase("set_api_key"));
        apiKeyInput.value = ''; // Clear the input field after pressing Enter
        ModelSelect.hidden = !ModelSelect.hidden;
        apiKeyInput.hidden = !apiKeyInput.hidden;
    }
})
     //=== for selecting subpart ===//
const ModelObserver = new MutationObserver(async ()=>{
    if(!ModelSelect.hidden){
        const response = await fetch(AddBase("get_model_list"));
        const data = await response.json();
        const list = data.models;
        
        //deal with the display of the list
        ModelSelect.innerHTML = ''; // Clear existing options
        const default_op = document.createElement('option');
        default_op.value = 'Please select a model';
        default_op.textContent = 'Please select a model';
        default_op.disabled = true;
        default_op.selected = true;
        ModelSelect.appendChild(default_op);

        list.forEach(model => {
            const option = document.createElement('option');
            option.value = model;
            option.textContent = model;
            ModelSelect.appendChild(option);
        });
    }
}) 
ModelObserver.observe(ModelSelect, { attributes: true, attributeFilter: ['hidden'] });
ModelSelect.addEventListener('change', () => {
    console.log('Activated')
    ModelSelect.hidden = !ModelSelect.hidden;
    setAPIKeyButton.hidden = !setAPIKeyButton.hidden;
    sendMessage(ModelSelect.value,AddBase("set_model"));
})

export default optionReader;