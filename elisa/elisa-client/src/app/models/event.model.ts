import {Collision} from './collision.model';
import {Course} from './course';
import {Room} from './room';
import {Group} from './group';

enum Days{
  "monday" = 1,
  "tuesday" = 2,
  "wednesday" = 3,
  "thursday" = 4,
  "friday" = 5,
}

export class Event {
  id: string;
  idType: number;
  course: Course;
  teacher: any;
  rooms: Room[];
  groups: Group[];
  day: string;
  startTime: number;
  endTime: number;
  collisions: Collision[];
  status: string;
  color: string;


  constructor(id: string, idType: number, idCourse: Course, idTeacher: number, idRoom: Room[], day: string, startTime: number, endTime: number, groups: Group[], status : string, color : string) {
    this.id = id;
    this.idType = idType;
    this.course = idCourse;
    this.teacher = idTeacher;
    this.rooms = idRoom;
    this.day = day;
    this.startTime = startTime;
    this.endTime = endTime;
    this.collisions = [];
    this.groups = groups;
    this.status = status;
    this.color = color;
  }

  generateEventCalendar(){

    let endTime = new Date();
    endTime.setHours(this.endTime,0,0,0);
    let startTime = new Date();
    startTime.setHours(this.startTime,0,0,0);

    let calendarEvent = {
      id: this.id,
      idType: this.idType,
      status: this.status,
      title: this.course.code + ' ' + this.teacher.last_name,
      startTime: startTime.toLocaleTimeString('sk-SK'),
      endTime: endTime.toLocaleTimeString('sk-SK'),
      resourceId: this.day,
      color: this.color,
    };
    return calendarEvent;
  }

  generateExport(version){
    let rooms = [];
    this.rooms.forEach(room=>{
      rooms.push(room.id);
    });
    let groups = [];
    this.groups.forEach(group=>{
      groups.push(group.id);
    });
    let exportEvent = {
      "duration":{
        "start":this.startTime,
        "end":this.endTime,
      },
      "day": Days[this.day],
      "activity": {
        "category": this.idType,
        "courses" : [this.course.id]
      },
      "timetable": version,
      "teacher": this.teacher.id,
      "rooms": rooms,
      "groups": groups,
    };
    return exportEvent;
  }
}
