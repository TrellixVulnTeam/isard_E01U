// Theme
import 'primevue/resources/themes/saga-blue/theme.css';
// Core css
import 'primevue/resources/primevue.min.css';
// Icons
import 'primeicons/primeicons.css';
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import 'primeflex/primeflex.css';

import App from './App.vue';
import AppLayout from '@/layouts/AppLayout.vue';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import PanelMenu from 'primevue/panelmenu';
import Panel from 'primevue/panel';
import PrimeIcons from 'primevue/config';
import PrimeVue from 'primevue/config';
import Sidebar from 'primevue/sidebar';
import { createApp } from 'vue';
import router from './router';
import store from './store';

createApp(App)
  .use(store)
  .use(router)
  .use(PrimeVue)
  .use(PrimeIcons)
  .component('AppLayout', AppLayout)
  .component('PanelMenu', PanelMenu)
  .component('Panel', Panel)
  .component('InputText', InputText)
  .component('Dropdown', Dropdown)
  .component('Button', Button)
  .component('Card', Card)
  .component('Sidebar', Sidebar)
  .mount('#app');
