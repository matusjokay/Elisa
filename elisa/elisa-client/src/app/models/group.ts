import {Event} from './event.model';

export class Group {
  public id: number;
  public name: string;
  public abbr: string;
  public parent: number;
  public children: number[];
  public events: Event[];
  // constructor(
  //   public id: number,
  //   public name: string,
  //   public abbr: string,
  //   public parent: number,
  //   public children: number[],
  //   public events: Event[],
  // ) {  }
  constructor(){}
}
