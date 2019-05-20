import {Department} from './department';

export class Course {
  public id: number;
  public name: string;
  public code: string;
  public completion: string;
  public department?: number;
  public departmentObject?: Department;
  public id_teacher: number;
  public teacher_name: string;
  constructor(
  ) {  }
}
