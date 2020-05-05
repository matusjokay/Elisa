import {Component, ElementRef, OnInit, ViewChild} from '@angular/core';
import resourceTimelinePlugin from "@fullcalendar/resource-timeline";
import interactionPlugin, {Draggable} from '@fullcalendar/interaction';
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
import {Collision} from '../../../../models/collision.model';
import { MatDialog } from '@angular/material/dialog';
import {EventDetailComponent} from '../../../../components/event-detail/event-detail.component';
import { User } from 'src/app/models/user';

@Component({
  selector: 'app-timetable-update-main',
  templateUrl: './timetable-update-main.component.html',
  styleUrls: ['./timetable-update-main.component.less']
})
export class TimetableUpdateMainComponent implements OnInit {
  @ViewChild('groupCalendar') groupCalendar: TimetableComponent;
  @ViewChild('roomCalendar') roomCalendar: TimetableComponent;
  @ViewChild('userCalendar') userCalendar: TimetableComponent;
  Days = {
    1: "monday",
    2: "tuesday",
    3: "wednesday",
    4: "thursday",
    5: "friday",
  };
  courses: Course[];
  teachers: any;
  rooms: Room[];
  requirements: Requirement[];
  groups: Group[];
  events: Event[];
  collisions: any = [];

  newEvents: Event[] = [];
  newCollisions: Collision[] = [];
  updateEvents: Event[] = [];
  deleteEvents: string[] = [];

  newEventsCounter = 0;
  newCollisionsCounter = 0;
  parentCheck: boolean = false;
  childCheck: boolean = false;

  calendarOptions: any = [];

  activeSchema: string;
  activeVersion: number;
  activeActivityCategories;
  activeCourse: Course;
  activeTeacher: any;
  activeGroups: Group[] = [];
  activeRoom: Room;

  @ViewChild('externals') externals: ElementRef;
  private activeRequirement: any[];

  constructor(
    private userService: UserService,
    private roomService: RoomService,
    private groupService: GroupService,
    private courseService: CourseService,
    private requirementService: RequirementService,
    private timetableService: TimetableService,
    public dialog: MatDialog
    ) { }

  ngOnInit() {
    this.calendarOptions = {
      height: 'parent',
      events: [
      ],
      editable: true,
      eventClick: true,
      droppable: true,
      plugins: [resourceTimelinePlugin,interactionPlugin],
    };
    this.activeVersion = 1;
    this.getDefaultVersion();
    // this.getData(1);
  }

  getDefaultVersion(){
    this.timetableService.getTimetableVersionLatest().subscribe((version: any) => {
      this.activeVersion = version.id;
      this.getData();
    });
  }

  /**
   * loading necessary data
   */
  getData(){
    this.loadUsers();
  }

  loadUsers(){
    this.userService.getAllMap().subscribe(result=>{
      this.teachers = result;
      this.loadRooms()
    });
  }
  loadRooms(){
    this.roomService.getAllMap().subscribe(result=>{
      this.rooms = result;
      this.loadGroups();
    });
  }
  loadGroups(){
    this.groupService.getAllMap().subscribe(result=>{
      this.groups = result;
      this.loadCourses();
    });
  }
  loadCourses(){
    this.courseService.getCoursesByTeacherMap().subscribe(result=>{
      this.courses = result;
      this.loadRequirements();
    })

  }
  loadRequirements(){
      this.requirementService.getAll().subscribe(result=>{
        this.requirements = result;
        this.loadActivitiesGroups();
      });

  }
  loadActivitiesGroups(){
    this.timetableService.getActivitiesGroup().subscribe(result=>{
      this.activeActivityCategories = result;
      this.loadEvents();
      new Draggable(this.externals.nativeElement,{itemSelector: '.fc-event'});
    });
  }
  loadEvents(){
      this.timetableService.getAllEvents(this.activeVersion).subscribe(result=>{
        console.log(result);
        this.events = result.map(event=>{
          let rooms: Room[] = [];
          event.rooms.forEach(room=>{
            rooms.push(this.rooms[room]);
          });
          let groups: Group[] = [];
          event.groups.forEach(group=>{
            groups.push( this.groups[group]);
          });
          let parsedEvent = new Event(
            event.id,
            event.activity.category,
            this.courses[event.activity.courses[0]],
            this.teachers[event.teacher],
            rooms,
            this.Days[event.day],
            event.duration.lower,
            event.duration.upper,
            groups,
            "old",
            this.activeActivityCategories.find(category => category.id === event.activity.category).color
            );
          return parsedEvent;
        });
        console.log(this.events);
        this.loadCollisions();
      });

  }
  loadCollisions(){
      this.timetableService.getAllCollisions(this.activeVersion).subscribe(result=>{
        this.collisions = result;
        this.parseRequirements();
        this.parseEvents();
      });
  }

  /**
   * drop extrenal event to calendar
   * @param arg
   */
  dropEvent(arg){
    this.newEventsCounter++;
    let rooms: Room[] = [];
    rooms.push(this.rooms[this.activeRoom.id]);
    let event = new Event(
      "new"+this.newEventsCounter,
      arg.draggedEl.getAttribute('data-type'),
      this.courses[this.activeCourse.id],
      this.teachers[this.activeTeacher.id],
      rooms,
      arg.resource.id,
      arg.date.getHours(),
      arg.date.getHours()+1,
      this.activeGroups.filter(group=>{return this.groups[group.id]}),
      'new',
      arg.draggedEl.getAttribute('data-color'),
    );

    let calendarEvent = event.generateEventCalendar();

    this.groupCalendar.addEvent(calendarEvent);
    this.roomCalendar.addEvent(calendarEvent);
    this.userCalendar.addEvent(calendarEvent);

    this.events[event.id] = event;
    this.newEvents.push(this.events[event.id]);

    this.activeTeacher['events'].push(event);
    this.activeRoom['events'].push(event);
    this.activeGroups.forEach(
      (group: Group) =>{
        group.events.push(event)
      }
    );
    this.detectCollisions(event);
  }

  /**
   * resize event, change time
   * @param arg
   */
  resizeEvent(arg){
    let event = this.events[arg.event.id];
    event.startTime = arg.event.start.getHours();
    event.endTime = arg.event.end.getHours();
    this.events[arg.event.id]['startTime'] = arg.event.start.getHours();
    this.events[arg.event.id]['endTime'] = arg.event.end.getHours();

    let calendarEvent = event.generateEventCalendar();

    /**
     * if event is not new or wasn't updated add it to array for updates
     */
    if(event.status !== 'new' && this.updateEvents.indexOf(event) === -1){
      this.updateEvents.push(event);
    }
    this.userCalendar.updateEvent(arg.event,calendarEvent);
    this.roomCalendar.updateEvent(arg.event,calendarEvent);
    this.groupCalendar.updateEvent(arg.event,calendarEvent);

    this.removeEventFromCollisions(event);
    this.detectCollisions(event);
  }

  /**
   * drag events in calendar
   * @param arg
   */
  dragEvent(arg){
    let event = this.events[arg.event.id];
    event.startTime = arg.event.start.getHours();
    event.endTime = arg.event.end.getHours();
    event.day = arg.newResource ? arg.newResource.id :this.events[arg.event.id]['day'];

    this.groupCalendar.updateEvent(arg.event,event.generateEventCalendar());
    this.userCalendar.updateEvent(arg.event,event.generateEventCalendar());
    this.roomCalendar.updateEvent(arg.event,event.generateEventCalendar());

    if(event.status !== 'new' && this.updateEvents.indexOf(event) === -1){
      this.updateEvents.push(event);
    }
    this.removeEventFromCollisions(event);
    this.detectCollisions(event);
  }

  /**
   * show event details
   * @param arg
   */
  clickEvent(arg){
    let event = this.events[arg.event.id];

    const dialogRef = this.dialog.open(EventDetailComponent, {
      width: '800px',
      disableClose: true,
      data: {'event': event, 'rooms': this.rooms}
    });

    dialogRef.afterClosed().subscribe(result => {
        if(result){
          this.events[arg.event.id] = result;
        }
        else{
          // this.teachers[arg.event.teacher.id].events.splice(this.teachers[arg.event.teacher.id].event.indexOf(result),1)
          event.teacher.events.splice(event.teacher.events.indexOf(event),1);
          event.rooms.forEach((room:Room) =>{
            room.events.splice(room.events.indexOf(event),1);
          });

          event.groups.forEach((group:Group) =>{
            group.events.splice(group.events.indexOf(event),1);
          });
          if(event.status !== 'new'){
            this.deleteEvents.push(event.id);
          }
          delete this.events[arg.event.id];
          this.reloadCourse();
          this.reloadRoom();
          this.groupsChange();
        }
    });

  }

  /**
   * set course
   * @param id
   */
  courseChange(id){
    if (this.activeCourse !== id) {
      this.activeCourse = this.courses[id];
      const teacher = this.courses[id].teacher;
      if (teacher instanceof User) {
        this.activeTeacher = this.teachers[teacher.id];
      } else {
        this.activeTeacher = this.teachers[teacher];
      }
    }
    this.reloadCourse();
  }

  /**
   * load event for calendar after course change
   */
  reloadCourse(){

    let requirement: Requirement;
    if(this.activeTeacher.requirements[this.activeCourse.id]){
      requirement = this.activeTeacher.requirements[this.activeCourse.id];
      this.activeRequirement = this.generateEventCalendar(requirement);
    }
    else if(this.activeTeacher.requirements['all']){
      requirement = this.activeTeacher.requirements['all'];
      this.activeRequirement = this.generateEventCalendar(requirement);
    }
    else{
      requirement = null;
      this.activeRequirement = null;
    }
    let events = this.activeTeacher.events.map((event: Event) => {
      return event.generateEventCalendar();
    });

    if(this.activeRequirement){
      events = events.concat(this.activeRequirement);
    }
    this.userCalendar.setEvents(events);
    if(this.activeRoom){
      this.reloadRoom();
    }
    if(this.groups){
      this.groupsChange();
    }
  }

  Types = {
    1 : "green",
    2 : "yellow",
    3 : "red",
  };

  generateEventCalendar(requirement){
    let calendarEvents: any[] = [];
    requirement.events.forEach(obj =>{
      let calendarEvent = {
        startTime: obj.start,
        endTime: obj.end,
        resourceId: this.Days[obj.day],
        rendering: 'background',
        backgroundColor: this.Types[obj.type],
      };
      calendarEvents.push(calendarEvent);
    });
    return calendarEvents;
  }

  /**
   * change room
   * @param id
   */
  roomChange(id){
    if(this.activeCourse != id){
      this.activeRoom = this.rooms[id];
    }
    this.reloadRoom();
  }

  /**
   * load events for calendar after room change
   */
  reloadRoom(){
    let events = this.activeRoom.events.map((event: Event) => {
      return event.generateEventCalendar();
    });
    if(this.activeRequirement){
      events = events.concat(this.activeRequirement);
    }
    this.roomCalendar.setEvents(events);
  }

  /**
   * add new group
   * @param id
   */
  addGroup(id){
    this.activeGroups.push(this.groups[id]);
    this.groupsChange();
  }

  /**
   * remove group
   * @param id
   */
  removeGroup(id){
    this.activeGroups.splice(this.activeGroups.map(function(group) {return group.id}).indexOf(id),1);
    this.groupsChange();
  }

  /**
   * show parents event of chosen groups
   * @param event
   */
  showParent(event){
    this.parentCheck = event.checked;
    this.groupsChange();
  }

  /**
   * show childs events of chosen groups
   * @param event
   */
  showChild(event){
    this.childCheck = event.checked;
    this.groupsChange();
  }

  /**
   * reload calendar events of groups
   */
  groupsChange(){
    let events = [];
    this.activeGroups.forEach((group: Group)=> {
      group.events.forEach((event: Event) =>{
        console.log(events);
        let calendarEvent = event.generateEventCalendar();
        console.log(calendarEvent);
        console.log("vysledok iffu");
        console.log(events.indexOf(calendarEvent) === -1);
        if(events.findIndex(x=> x.id == calendarEvent.id) === -1){
          events.push(calendarEvent);
        }
      });
      if(this.parentCheck){
        this.getChildEvents(group)
        let parentGroup: Group = group;
        while(this.groups[parentGroup.parent]){
          parentGroup = this.groups[parentGroup.parent];
          parentGroup.events.forEach((event: Event) =>{
            let calendarEvent = event.generateEventCalendar();
            if(events.findIndex(x=> x.id == calendarEvent.id) === -1){
              events.push(calendarEvent);
            }
          });
        }
      }
      if(this.childCheck){
        let childrenEvents = [];
        group.children.forEach(childGroupId =>{
          this.getChildEvents(this.groups[childGroupId]).forEach(event =>{
            childrenEvents.push(event);
          })
        });
        childrenEvents.forEach(event =>{
          if(events.findIndex(x=> x.id == event.id) === -1){
            events.push(event);
          }
        })
      }
    });
    if(this.activeRequirement){
      events = events.concat(this.activeRequirement);
    }
    this.groupCalendar.setEvents(events);
  }

  private getChildEvents(group: Group){
    let calendarEvents = [];
    group.events.forEach((event: Event) =>{
      let calendarEvent = event.generateEventCalendar();
      calendarEvents.push(calendarEvent);
    });
    if(group.children){
      group.children.forEach((childId:number) => {
        calendarEvents.push(this.getChildEvents(this.groups[childId]));
      });
    }
    return calendarEvents;
  }

  /**
   * parse requirements by teacher
   */
  private parseRequirements() {
    // this.requirements.forEach(obj =>{
    //   let index = (obj.course ? obj.course.toString() : "all");
    //   // this.teachers[obj.teacher]['requirements'][index] = obj;
    //   this.teachers[this.courses[obj.course].id_teacher]['requirements'][index] = obj;
    // });
  }

  /**
   * parse events
   */
  private parseEvents() {

    this.events.forEach((event: Event)=>{
      event.teacher.events.push(event);

      event.rooms.forEach(room=>{
        room.events.push(event);
      });

      event.groups.forEach(group=>{
        group.events.push(event);
      });
    });
  }

  /**
   * detect collision after event change
   * @param event
   */
  private detectCollisions(event : Event) {
    event.teacher['events'].forEach(teacherEvent => {
      this.compareEvents(teacherEvent, event, 'teacher');
      }
    );

    event.rooms.forEach(room => {
     room.events.forEach(roomEvent => {
          this.compareEvents(roomEvent, event, 'room');
        }
      );
    });

    event.groups.forEach(group => {
     group.events.forEach(groupEvent => {
          this.compareEvents(groupEvent, event, 'group');
        }
      );
    });
  }

  /**
   * compare events for collisions
   * @param event
   * @param newEvent
   * @param type
   */
  private compareEvents(event,newEvent,type){
    if(event.day === newEvent.day && event.id != newEvent.id){
      if((event.startTime < newEvent.endTime && event.endTime >= newEvent.endTime)
        || (event.startTime <= newEvent.startTime && event.endTime > newEvent.startTime)
        || (event.startTime > newEvent.startTime && event.endTime < newEvent.endTime)
      ){
        let start = Math.max(event.startTime,newEvent.startTime);
        let end = Math.min(event.endTime,newEvent.endTime);

        let collisions: Collision[] = [];
        if(event.collisions){
          collisions = event.collisions.filter( collision => {
            if((collision.type === type)
                && ((collision.start < end && collision.end >= end)
                    || (collision.start <= start && collision.end > start)
                    || (collision.start > start && collision.end < end))
            ){
              if((collision.events.indexOf(newEvent) === -1)){
                collision.events.push(newEvent);
                newEvent.collisions.push(collision);
                collision.start = Math.max(event.startTime,newEvent.startTime);
                collision.end = Math.min(event.endTime,newEvent.endTime);
                collision.status = "unresolved";
              }
              return collision;
            }
          });
        }
        if (collisions.length === 0){
          let collision: Collision;
          this.newCollisionsCounter++;
          collision = new Collision();
          collision.start = start;
          collision.end = end;
          collision.events = [];
          collision.events.push(event);
          collision.events.push(newEvent);
          newEvent.collisions.push(collision);
          event.collisions.push(collision);
          collision.type = type;
          collision.status = "unresolved";
          this.collisions.push(collision);
          this.newCollisions.push(collision);
        }
      }
    }
  }

  private removeEventFromCollisions(event : Event){
    let collisions = event.collisions;

    collisions.filter(collision => {
      if (collision.removeEvent(event)){
        this.collisions.splice(this.collisions.indexOf(collision),1);
      }
    });
    event.collisions = [];
  }

  /**
   * send data to server
   */
  saveData(){
    // check new events
    if(this.newEvents){
      let newEventsExport = [];
      this.newEvents.forEach((event: Event) => {
        newEventsExport.push(event.generateExport(this.activeVersion));
      });
      this.timetableService.saveEvents(newEventsExport,1).subscribe(result =>{
        for(let index = 0; index < result.length; index++){
          let oldId = this.newEvents[index].id;
          this.newEvents[index].id = result[index].id;
          this.events[result[index].id] = this.newEvents[index];
          delete this.events[oldId];
        }
      });
    }

    // check updated events
    if(this.updateEvents){
      this.updateEvents.forEach((event: Event) => {
        this.timetableService.updateEvent(event.generateExport(this.activeVersion),this.activeVersion).subscribe();
      });
    }

    // delete events
    if(this.deleteEvents){
      this.deleteEvents.forEach(eventId =>{
        this.timetableService.deleteEvent(this.activeVersion,eventId).subscribe();
      });
      this.deleteEvents = [];
    }

    // create new collision events
    if(this.newCollisions){
      let newCollisionsExport = [];
      this.newCollisions.forEach((collision: Collision) => {
        newCollisionsExport.push(collision.generateExport(this.activeVersion));
      });
      this.timetableService.saveCollision(newCollisionsExport,this.activeVersion).subscribe();
    }
  }

  /**
   * create new version of timetable scheme
   */
  createNewVersion(){
    let body = {
      name: "new_version"
    }
    // this.timetableService.createVersion(body).subscribe();
  }

  /**
   * publish scheme
   */
  finalizeTimetable(){
    this.timetableService.finalizeVersion(this.activeVersion).subscribe();
  }
}
