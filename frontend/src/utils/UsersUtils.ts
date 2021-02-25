export default class UsersUtils {
  static cleanUsers(items: any[]): Types.User[] {
    console.log(items, 'items');
    return items.map(
      (item: any): Types.User => {
        return {
          userName: item.username,
          name: item.name,
          surname1: item.surname,
          email: '',
          surname2: '',
          status: '',
          organizationId: '',
          roles: [],
          lastAttempt: '',
          creationDate: '',
          uuid: item.uuid,
          id: '',
          avatar: '',
          profile: ''
        };
      }
    );
  }
}