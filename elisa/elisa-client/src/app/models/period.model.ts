import { Department } from './department';

export interface Period {
  id?: number;
  name: string;
  university_period: number;
  academic_sequence: number;
  previous_period?: number;
  next_period?: number;
  start_date: Date;
  end_date: Date;
  active: boolean;
  department: number | Department;
}
