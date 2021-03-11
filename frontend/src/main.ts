// Theme
import 'primevue/resources/themes/saga-blue/theme.css';
// Core css
import 'primevue/resources/primevue.min.css';
// Icons
import 'primeicons/primeicons.css';
import 'primevue/resources/themes/bootstrap4-light-blue/theme.css';
import 'primeflex/primeflex.css';
import '@/assets/layout/layout.scss';

import App from './App.vue';
import AppLayout from '@/layouts/AppLayout.vue';
import Button from 'primevue/button';
import Calendar from 'primevue/calendar';
import Card from 'primevue/card';
import Column from 'primevue/column';
import DataTable from 'primevue/datatable';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Panel from 'primevue/panel';
import PanelMenu from 'primevue/panelmenu';
import PrimeIcons from 'primevue/config';
import PrimeVue from 'primevue/config';
import RadioButton from 'primevue/radiobutton';
import Sidebar from 'primevue/sidebar';
import VueAxios from 'vue-axios';
import axios from 'axios';
import { createApp } from 'vue';
import i18n from '@/i18n';
import router from './router';
import { store } from './store';
import { ActionTypes } from './store/actions';
import { getCookie } from 'tiny-cookie';
import ConnectionService from './service/ConnectionService';

ConnectionService.setClientBackend();
const app = createApp(App);
app.use(store);
app.use(router);
app.use(i18n);
app.use(PrimeVue);
app.use(PrimeIcons);
app.use(VueAxios, axios);

app.component('AppLayout', AppLayout);
app.component('PanelMenu', PanelMenu);
app.component('RadioButton', RadioButton);
app.component('Panel', Panel);
app.component('Calendar', Calendar);
app.component('InputText', InputText);
app.component('Dropdown', Dropdown);
app.component('Button', Button);
app.component('Card', Card);
app.component('Sidebar', Sidebar);
app.component('DataTable', DataTable);
app.component('Column', Column);
app.mount('#app');

router.beforeEach((to, from, next) => {
  const loggedIn = store.getters.loginToken;
  const tokenCookie: string = getCookie('token') || '';

  // Parse Url
  const urlParts = to.fullPath.split('?');
  const url = urlParts[0]; // Url without params
  const urlParams = urlParts[1]; // Params to use in search

  const urlSegments = url.split('/');
  const detailId = urlSegments.length > 2 ? urlSegments[2] : '';
  const section = urlSegments[1];

  if (!loggedIn) {
    if (tokenCookie && tokenCookie != 'null' && tokenCookie != '') {
      // Has token, check if it's valid or refresh!!!!!

      store
        .dispatch(ActionTypes.REFRESH_TOKEN_FROM_SESSION, {
          token: tokenCookie
        })
        .then(() => {
          if (detailId && detailId.length > 0) {
            store.dispatch(ActionTypes.GET_ITEM, {
              section,
              params: { id: detailId }
            });
          } else {
            store.dispatch(ActionTypes.NAVIGATE, {
              section,
              params: { id: detailId }
            });
          }
        });
    } else if (to.meta.needsAuth) {
      // No token && needs auth
      console.log('***** No hay token && needs auth *****');
      router.push({ name: 'login' });
    } else {
      // no token && no auth
      console.log(to, '**** Open ****');
      store.dispatch(ActionTypes.SET_NAVIGATION_DATA, {
        section: to.name,
        url: to.fullPath,
        queryParams: [],
        editmode: false
      });
      next();
    }
  } else {
    // logged in
    console.log(to, '***** Logged in *****');
    store.dispatch(ActionTypes.SET_NAVIGATION_DATA, {
      section,
      params: { id: detailId },
      url: to.path,
      queryParams: [],
      editmode: false
    });
    next();
  }
});
