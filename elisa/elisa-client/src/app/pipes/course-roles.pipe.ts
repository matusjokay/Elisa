import { Pipe, PipeTransform } from '@angular/core';
import { CourseUserRole, CourseRole } from '../models/course-users.model';

@Pipe({
  name: 'courseRolesShow'
  // name: 'courseRolesShow',
  // pure: false
})
export class CourseRolesPipe implements PipeTransform {

  transform(userCourseRoles: CourseUserRole[], allCourseRoles: CourseRole[]): any {
    const resultArray = [];
    userCourseRoles.forEach(row => {
      const roleObj = allCourseRoles.find(role => row.roleId === role.id);
      resultArray.push(roleObj);
    });
    return resultArray;
  }

}
