import { ActionContext, ActionTree } from 'vuex';
import { MutationTypes, Mutations } from './mutations';

import LoginService from '@/service/LoginService';
import SearchService from '@/service/SearchService';
import { State } from './state';
import UserService from '@/service/UserService';
import UsersUtils from '@/utils/UsersUtils';
import router from '@/router';
import { store } from '.';
import { refreshClient } from '@/main';

const loginService = new LoginService();
const searchService = new SearchService();

type AugmentedActionContext = {
  commit<K extends keyof Mutations>(
    key: K,
    payload: Parameters<Mutations[K]>[1]
  ): ReturnType<Mutations[K]>;
} & Omit<ActionContext<State, State>, 'commit'>;

/* Action Enum*/

export enum ActionTypes {
  DO_LOCAL_LOGIN = 'DO_LOCAL_LOGIN',
  REFRESH_CLIENT_TOKEN = 'REFRESH_CLIENT_TOKEN',
  DO_SEARCH = 'DO_SEARCH',
  GO_SEARCH = 'GO_SEARCH',
  TOGGLE_MENU = 'TOGGLE_MENU',
  CHANGE_MENU_TYPE = 'CHANGE_MENU_TYPE',
  CHANGE_MENU_COLOR_MODE = 'CHANGE_MENU_COLOR_MODE',
  CHANGE_MENU_OVERLAY_ACTIVE = 'CHANGE_MENU_OVERLAY_ACTIVE',
  CHANGE_MENU_MOBILE_ACTIVE = 'CHANGE_MENU_MOBILE_ACTIVE',
  CHANGE_MENU_STATIC_INACTIVE = 'CHANGE_MENU_STATIC_INACTIVE'
}

/* Action Types*/
export interface Actions {
  [ActionTypes.DO_LOCAL_LOGIN](
    { commit }: AugmentedActionContext,
    payload: { usr: string; psw: string; entity: string }
  ): void;

  [ActionTypes.DO_SEARCH](
    { commit }: AugmentedActionContext,
    payload: {
      section: string;
      query: string;
      queryParams: string[];
      size: number;
      start: number;
    }
  ): void;

  [ActionTypes.REFRESH_CLIENT_TOKEN](
    { commit }: AugmentedActionContext,
    payload: {
      token: string;
    }
  ): void;

  [ActionTypes.GO_SEARCH](
    { commit }: AugmentedActionContext,
    payload: {
      section: string;
      url: string;
      queryParams: string[];
      editmode: boolean;
    }
  ): void;

  [ActionTypes.TOGGLE_MENU](
    { commit }: AugmentedActionContext,
    payload: {}
  ): void;

  [ActionTypes.CHANGE_MENU_TYPE](
    { commit }: AugmentedActionContext,
    payload: string
  ): void;

  [ActionTypes.CHANGE_MENU_COLOR_MODE](
    { commit }: AugmentedActionContext,
    payload: string
  ): void;

  [ActionTypes.CHANGE_MENU_OVERLAY_ACTIVE](
    { commit }: AugmentedActionContext,
    payload: boolean
  ): void;

  [ActionTypes.CHANGE_MENU_MOBILE_ACTIVE](
    { commit }: AugmentedActionContext,
    payload: boolean
  ): void;

  [ActionTypes.CHANGE_MENU_STATIC_INACTIVE](
    { commit }: AugmentedActionContext,
    payload: boolean
  ): void;
}

/****** ACTIONS ****/
export const actions: ActionTree<State, State> & Actions = {
  [ActionTypes.DO_LOCAL_LOGIN]({ commit }, payload) {
    loginService
      .doLogin(payload.usr, payload.psw, 'local', payload.entity)
      .then((response: any): any => {
        const payload = { token: response };

        store.dispatch(ActionTypes.REFRESH_CLIENT_TOKEN, payload);

        router.push({ name: 'users' });
      });
  },

  [ActionTypes.REFRESH_CLIENT_TOKEN]({ commit }, payload) {
    refreshClient(payload.token);
    commit(MutationTypes.LOGIN_SUCCESS, payload);
  },

  [ActionTypes.DO_SEARCH]({ commit }, payload) {
    searchService
      .listSearch(
        payload.section,
        payload.query,
        payload.queryParams,
        payload.size,
        payload.start
      )
      .then((response: any): any => {
        commit(MutationTypes.LOAD_LIST_ITEMS, UsersUtils.cleanUsers(response));
      });
  },

  [ActionTypes.GO_SEARCH]({ commit }) {
    router.push({ name: 'users' });
  },

  [ActionTypes.TOGGLE_MENU]({ commit }) {
    commit(MutationTypes.TOGGLE_MENU, {});
  },

  [ActionTypes.CHANGE_MENU_TYPE]({ commit }, payload: string) {
    commit(MutationTypes.CHANGE_MENU_TYPE, payload);
  },

  [ActionTypes.CHANGE_MENU_COLOR_MODE]({ commit }, payload: string) {
    commit(MutationTypes.CHANGE_MENU_COLOR_MODE, payload);
  },

  [ActionTypes.CHANGE_MENU_OVERLAY_ACTIVE]({ commit }, payload: boolean) {
    commit(MutationTypes.CHANGE_MENU_OVERLAY_ACTIVE, payload);
  },

  [ActionTypes.CHANGE_MENU_MOBILE_ACTIVE]({ commit }, payload: boolean) {
    commit(MutationTypes.CHANGE_MENU_MOBILE_ACTIVE, payload);
  },

  [ActionTypes.CHANGE_MENU_STATIC_INACTIVE]({ commit }, payload: boolean) {
    commit(MutationTypes.CHANGE_MENU_STATIC_INACTIVE, payload);
  }
};