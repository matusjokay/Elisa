import { User } from './user';
import { Department } from './department';

export class Course {
  id?: number;
  name: string;
  code: string;
  department: number | Department;
  teacher?: number | User;
  completion: string;
  period: number;
  public constructor(init?: Partial<Course>) {
    Object.assign(this, init);
  }
}
