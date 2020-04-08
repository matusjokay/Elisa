/**
 * Helper class which stores statically
 * different types of roles from the server.
 * Each object instance holds RoleAuth authorization
 * object type which manages access to different
 * navigation menu items, buttons pages and other
 * access points of the client.
 */
export class RoleManager {

  public static readonly MAIN_TIMETABLE_CREATOR = {
   id: 1,
   name: 'MAIN_TIMETABLE_CREATOR',
   authorization : {
     creating: true,
     updating: true,
     deleting: true,
     requesting: true,
     managing: true,
   }
  };

  public static readonly LOCAL_TIMETABLE_CREATOR = {
    id: 2,
    name: 'LOCAL_TIMETABLE_CREATOR',
    authorization : {
     creating: true,
     updating: true,
     deleting: false,
     requesting: true,
     managing: true,
   }
  };

  public static readonly TEACHER = {
    id: 3,
    name: 'TEACHER',
    authorization : {
     creating: false,
     updating: false,
     deleting: false,
     requesting: true,
     managing: true,
   }
  };

  public static readonly STUDENT = {
    id: 4,
    name: 'STUDENT',
    authorization : {
     creating: false,
     updating: false,
     deleting: false,
     requesting: true,
     managing: false,
   }
  };

  public static readonly ALL = [1, 2, 3, 4];

  /** Function to create authorization object
   * from all of users provided roles.
   * @param roles An array of Role IDs
   * @returns A single RoleAuth object for specific
   * component/page
   */
  public static setRolePrivileges(roles: number[]): RoleAuth {
    const authorization = {};
    const authorizations = [];
    roles.forEach(role => {
      switch (role) {
        case RoleManager.MAIN_TIMETABLE_CREATOR.id:
          authorizations.push(RoleManager.MAIN_TIMETABLE_CREATOR.authorization);
          break;
        case RoleManager.LOCAL_TIMETABLE_CREATOR.id:
          authorizations.push(RoleManager.LOCAL_TIMETABLE_CREATOR.authorization);
          break;
        case RoleManager.TEACHER.id:
          authorizations.push(RoleManager.TEACHER.authorization);
          break;
        case RoleManager.STUDENT.id:
          authorizations.push(RoleManager.STUDENT.authorization);
          break;
      }
    });

    // construct authorization object with privileges
    authorizations.forEach(auth => {
      Object.keys(auth).forEach(key => authorization[key] = !authorization[key] ?
      auth[key] : authorization[key]);
    });
    return authorization;
  }

  /** Helper function to retrieve Role objects
   * for displaying users Role names.
   * @param roles An array of users Role IDs
   * @returns Array of Role objects which contains
   * the name of user roles
   */
  public static getRoleObjects(roles: number[]): Role[] {
    const roleArray = [];
    roles.forEach(role => {
      switch (role) {
        case RoleManager.MAIN_TIMETABLE_CREATOR.id:
          roleArray.push({
            id: RoleManager.MAIN_TIMETABLE_CREATOR.id,
            name: RoleManager.MAIN_TIMETABLE_CREATOR.name,
          });
          break;
        case RoleManager.LOCAL_TIMETABLE_CREATOR.id:
          roleArray.push({
            id: RoleManager.LOCAL_TIMETABLE_CREATOR.id,
            name: RoleManager.LOCAL_TIMETABLE_CREATOR.name,
          });
          break;
        case RoleManager.TEACHER.id:
          roleArray.push({
            id: RoleManager.TEACHER.id,
            name: RoleManager.TEACHER.name,
          });
          break;
        case RoleManager.STUDENT.id:
          roleArray.push({
            id: RoleManager.STUDENT.id,
            name: RoleManager.STUDENT.name,
          });
          break;
      }
    });
    return roleArray;
  }
}

export interface RoleAuth {
  creating?: boolean;
  updating?: boolean;
  deleting?: boolean;
  requesting?: boolean;
  managing?: boolean;
}

export interface Role {
  id: number;
  name?: string;
}
