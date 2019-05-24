import {Event} from './event.model';


export class Collision {
  public id: string;
  public events: Event[];
  public type: string;
  public start: number;
  public end: number;
  public status: string;
  public note: string;

  private calculateCollisionTime(){
    this.start  = Math.max.apply(Math, this.events.map(function(event) { return event.startTime; }));
    this.end    = Math.min.apply(Math, this.events.map(function(event) { return event.endTime; }));
  }

  removeEvent(event : Event){
    this.events.splice(this.events.indexOf(event),1);
    if (this.events.length > 1){
      this.calculateCollisionTime();
      return false;
    }
    else{
      let oldEvent : Event = this.events[0];
      oldEvent.collisions.splice(oldEvent.collisions.indexOf(this),1);
      return this;
    }
  }
}
