import {Department} from './department';

export interface Course {
  id: number;
  name: string;
  code: string;
  completion: string;
  department?: number;
  departmentObject?: Department;
  id_teacher: number;
  teacher_name: string;
}
