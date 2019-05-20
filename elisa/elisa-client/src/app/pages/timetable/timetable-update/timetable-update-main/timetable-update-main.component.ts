import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import resourceTimelinePlugin from "@fullcalendar/resource-timeline";
import interactionPlugin, {Draggable} from '@fullcalendar/interaction';
import {zip} from 'rxjs';
import {Course} from '../../../../models/course';
import {Room} from '../../../../models/room';
import {Requirement} from '../../../../models/requirement';
import {Group} from '../../../../models/group';
import {RequirementService} from '../../../../services/requirement.service';
import {UserService} from '../../../../services/user.service';
import {RoomService} from '../../../../services/room.service';
import {GroupService} from '../../../../services/group.service';
import {CourseService} from '../../../../services/course.service';
import {TimetableComponent} from '../../timetable/timetable.component';
import {TimetableService} from '../../../../services/timetable.service';
import {Event} from '../../../../models/event.model';

@Component({
  selector: 'app-timetable-update-main',
  templateUrl: './timetable-update-main.component.html',
  styleUrls: ['./timetable-update-main.component.less']
})
export class TimetableUpdateMainComponent implements OnInit {
  @ViewChild('groupCalendar') groupCalendar: TimetableComponent;
  @ViewChild('roomCalendar') roomCalendar: TimetableComponent;
  @ViewChild('userCalendar') userCalendar: TimetableComponent;
  courses: Course[];
  teachers: any;
  rooms: Room[];
  requirements: Requirement[];
  groups: Group[];
  events: Event[];
  collisions: any = [];
  newEventsCounter = 0;

  calendarOptions: any = [];

  activeSchema: string;
  activeVersion: string;
  activeActivityCategories;
  activeCourse;
  activeTeacher;
  activeGroups = [];
  activeRoom;

  @ViewChild('externals') externals: ElementRef;

  constructor(
    private userService: UserService,
    private roomService: RoomService,
    private groupService: GroupService,
    private courseService: CourseService,
    private requirementService: RequirementService,
    private timetableService: TimetableService,
    ) { }

  ngOnInit() {
    this.calendarOptions = {
      height: 'parent',
      events: [
      ],
      editable: true,
      // selectable: true,
      eventClick: true,
      droppable: true,
      plugins: [resourceTimelinePlugin,interactionPlugin],
    };

    // this.getDefaultVersion();
    this.getData(1);
  }

  getDefaultVersion(){
    this.timetableService.getLastScheme().subscribe(version =>{
      console.log(version);
    });
      // this.timetableService.getTimetableVersions().subscribe((version: any) => {
      //     this.activeVersion = version;
      //     this.getData(version);
      //     return version;
      // });
  }

  getData(version){
    zip(
      this.userService.getAllMap(),
      this.roomService.getAllMap(),
      this.groupService.getAllMap(),
      this.courseService.getCoursesByTeacherMap(),
      this.requirementService.getAll(),
      this.timetableService.getAllEvents(version),
      this.timetableService.getAllCollisions(version),
      this.timetableService.getActivitiesGroup(),
    ).subscribe(([usersData,roomsData, groupsData,coursesData,requirementsData,eventsData,collisionsData,activityCategories]) =>{
    // ).subscribe(([usersData,roomsData, groupsData,coursesData,requirementsData,activityCategories]) =>{
      this.teachers = usersData;
      this.rooms = roomsData;
      this.groups = groupsData;
      this.courses = coursesData;
      this.requirements = requirementsData;
      this.events = eventsData;
      this.events = [];
      this.collisions = collisionsData;
      this.collisions = [];
      this.activeActivityCategories = activityCategories;

      this.parseRequirements();
      this.parseEvents();
      new Draggable(this.externals.nativeElement,{itemSelector: '.fc-event'});
    });
  }

  dropEvent(arg){
    this.newEventsCounter++;
    let endTime = new Date();
    endTime.setHours(arg.date.getHours()+1,0,0,0);
    let calendarEvent = {
      id: "new"+this.newEventsCounter,
      idType: arg.draggedEl.getAttribute('data-type'),
      status: "new",
      idCourse: this.activeCourse['id'],
      idTeacher: this.activeTeacher['id'],
      idRoom: this.activeRoom['id'],
      title: this.activeCourse.name,
      startTime: arg.date.toLocaleTimeString('sk-SK'),
      endTime: endTime.toLocaleTimeString('sk-SK'),
      resourceId: arg.resource.id,
      color: arg.draggedEl.getAttribute('data-color'),
    };

    let event = new Event(
      "new"+this.newEventsCounter,
      arg.draggedEl.getAttribute('data-type'),
      this.activeCourse['id'],
      this.activeTeacher['id'],
      this.activeRoom['id'],
      arg.resource.id,
      arg.date.getHours(),
      arg.date.getHours()+1,
    );

    this.groupCalendar.addEvent(calendarEvent);
    this.roomCalendar.addEvent(calendarEvent);
    this.userCalendar.addEvent(calendarEvent);

    this.events[event.id] = event;
    this.detectCollisions(event);


    this.activeTeacher['events'].push(event.id);
    this.activeRoom['events'].push(event.id);
    this.activeGroups.forEach(
      groupId =>{
        this.groups[groupId]['events'].push(event.id)
      }
    )
  }

  resizeEvent(arg){
    let newEvent = {
      id: arg.event.id,
      idType: arg.event.extendedProps.idType,
      idCourse: arg.event.extendedProps.idCourse,
      idTeacher: arg.event.extendedProps.idTeacher,
      idRoom: arg.event.extendedProps.idRoom,
      status: arg.event.extendedProps.status,
      title: arg.event.title,
      startTime: arg.event.start.toLocaleTimeString('sk-SK'),
      endTime: arg.event.end.toLocaleTimeString('sk-SK'),
      resourceId: this.events[arg.event.id]['day'],
      color: arg.event.backgroundColor,
    };
    if(newEvent.idTeacher == this.activeTeacher.id){
      this.userCalendar.updateEvent(arg.event,newEvent);
    }
    if(newEvent.idRoom == this.activeRoom.id){
      this.roomCalendar.updateEvent(arg.event,newEvent);
    }
    // if(newEvent.idTeacher == this.activeTeacher.id){
      this.groupCalendar.updateEvent(arg.event,newEvent);
    // }

    this.events[newEvent.id]['startTime'] = arg.event.start.getHours();
    this.events[newEvent.id]['endTime'] = arg.event.end.getHours();

    this.detectCollisions(this.events[newEvent.id]);
  }

  dragEvent(arg){
    let newEvent = {
      id: arg.event.id,
      idType: arg.event.extendedProps.idType,
      idCourse: arg.event.extendedProps.idCourse,
      idTeacher: arg.event.extendedProps.idTeacher,
      idRoom: arg.event.extendedProps.idRoom,
      status: arg.event.extendedProps.status,
      title: arg.event.title,
      startTime: arg.event.start.toLocaleTimeString('sk-SK'),
      endTime: arg.event.end.toLocaleTimeString('sk-SK'),
      resourceId: arg.newResource ? arg.newResource.id :this.events[arg.event.id]['day'],
      color: arg.event.backgroundColor,
    };

      this.userCalendar.updateEvent(arg.event,newEvent);
      this.roomCalendar.updateEvent(arg.event,newEvent);
    this.groupCalendar.updateEvent(arg.event,newEvent);

    this.events[newEvent.id]['startTime'] = arg.event.start.getHours();
    this.events[newEvent.id]['endTime'] = arg.event.end.getHours();
    this.events[newEvent.id]['day'] = newEvent.resourceId;

    this.detectCollisions(this.events[newEvent.id]);
  }

  clickEvent(arg){
    // console.log(arg)
  }
  courseChange(id){
    if(this.activeCourse !== id){
      this.activeCourse = this.courses[id];
      this.activeTeacher = this.teachers[this.courses[id].id_teacher];
    }
  }

  roomChange(id){
    if(this.activeCourse != id){
      this.activeRoom = this.rooms[id];
    }
  }

  addGroup(id){
    this.activeGroups = this.activeGroups.concat(id);
  }

  private parseRequirements() {
    this.requirements.forEach(obj =>{
      this.teachers[obj.teacherId].requirements[(obj.courseId ? obj.courseId : "all")].push(obj);
    })
  }

  private parseEvents() {

  }

  private detectCollisions(event) {
    this.activeTeacher['events'].forEach(teacherEvent => {
      this.compareEvents(this.events[teacherEvent],event);
      }
    );
      // comparedEvents.push(this.activeTeacher['events']);

    //room collision

    //groups collision collision
  }

  private compareEvents(event,newEvent){
    if(event.day === newEvent.day && event.id != newEvent.id){
      if((event.startTime < newEvent.endTime && event.endTime >= newEvent.endTime)
        || (event.startTime <= newEvent.startTime && event.endTime <= newEvent.endTime)
        || (event.startTime > newEvent.startTime && event.endTime < newEvent.endTime)
      ){
        let start = Math.max(event.startTime,newEvent.startTime);
        let end = Math.min(event.endTime,newEvent.endTime);
        console.log('start: ', Math.max(event.startTime,newEvent.startTime), ' end:', Math.min(event.endTime,newEvent.endTime));
      }
    }
  }
}
