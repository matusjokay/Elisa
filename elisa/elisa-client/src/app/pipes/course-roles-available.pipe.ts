import { Pipe, PipeTransform } from '@angular/core';
import { CourseRole } from '../models/course-users.model';

@Pipe({
  name: 'courseRolesAvailable'
})
export class CourseRolesAvailablePipe implements PipeTransform {

  transform(allRoles: CourseRole[], assignedRoles: {idRow: number, roleId: number}[]): any {
    const resultArray = [];
    allRoles.forEach(role => {
      if (!assignedRoles.some(assignedRole => role.id === assignedRole.roleId)) {
        resultArray.push(role);
      }
    });
    return resultArray;
  }

}
