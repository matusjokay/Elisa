import {Equipment} from './equipment';
import {Department} from './department';
import {Event} from './event.model';

export class Room {
  public id: number;
  public name: string;
  public capacity: number;
  public category: string;
  public department: number;
  public departmentObject: Department;
  public events: Event[];
  public equipment: Equipment[];
  constructor() {  }
}
