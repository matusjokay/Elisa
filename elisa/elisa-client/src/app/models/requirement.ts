export class Requirement {
  public id: number;
  public userId: string;
  public teacher: string;
  public course: string;
  public events: any[];
  public note: string;
  public user_note: string;

  Days = {
    1: "monday",
    2: "tuesday",
    3: "wednesday",
    4: "thursday",
    5: "friday",
  };

  Types = {
  1 : "green",
  2 : "yellow",
  3 : "red",
  };

  generateEventCalendar(){
    console.log(this);
    let calendarEvents: any[];
    this.events.forEach(obj =>{
      let calendarEvent = {
        startTime: obj.start.toLocaleTimeString('sk-SK'),
        endTime: obj.end.toLocaleTimeString('sk-SK'),
        resourceId: this.Days[obj.day],
        rendering: 'background',
        backgroundColor: this.Types[obj.type],
      };
      calendarEvents.push(calendarEvent);
    });
    return calendarEvents;
  }
}
