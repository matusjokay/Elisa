import {Equipment} from './equipment';
import {Department} from './department';

export class Room {
  public id: number;
  public name: string;
  public capacity: number;
  public category: string;
  public department: number;
  public departmentObject: Department;
  public events: string[];
  public equipment: Equipment[];
  constructor() {  }
}
