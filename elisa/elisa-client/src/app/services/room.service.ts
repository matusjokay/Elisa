import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders, HttpParams} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map, share} from 'rxjs/operators';
import {Room, RoomType} from '../models/room';
import { BaseService } from './base-service.service';
import { RoomEquipment } from '../models/room-equipment';

@Injectable({
  providedIn: 'root'
})
export class RoomService {

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

  getAll(): Observable<Room[]>{
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get<Room[]>(environment.APIUrl + 'rooms/',options).
    pipe(
      map((data: Room[]) =>{
          return data;
        }
      ),share());
  }

  getAllMap(): Observable<Room[]>{
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get<Room[]>(environment.APIUrl + 'rooms/',options).
    pipe(
      map((data:any) =>{
        return data.reduce(function(r, e) {
          r[e.id] = e;
          r[e.id]["events"] = [];
          return r;
        }, {});
        }
      ),share());
  }

  deleteRoom(data: any) {

  }

  createRoom(post: any) {

  }

  updateRoom(post: any) {

  }

  getRoomTypes(): Observable<RoomType[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.get<RoomType[]>(`${environment.APIUrl}room-types/`,
      { headers: httpOptions });
  }

  getRoomsByType(typeId: number): Observable<Room[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    // Just for FEI
    const departmentId = 30;
    const params = new HttpParams()
      .set('department', departmentId.toString())
      .set('type', typeId.toString());
    return this.http.get<Room[]>(`${environment.APIUrl}rooms/get_rooms_by_department_and_type`,
      { headers: httpOptions, params: params });
  }

  getRoomsByIds(roomIds: number[]): Observable<Room[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    // Just for FEI
    const departmentId = 30;
    const params = new HttpParams()
      .set('department', departmentId.toString())
    return this.http.post<Room[]>(`${environment.APIUrl}rooms/get_rooms_by_department_and_ids/`,
      { rooms: roomIds }, { headers: httpOptions, params: params });
  }

  getRoomEquipmentByIds(roomIds: number[]): Observable<RoomEquipment[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.post<RoomEquipment[]>(`${environment.APIUrl}room-equipment/get_equipment_of_rooms/`,
      { rooms: roomIds }, { headers: httpOptions });
  }

  importCategoryRooms() {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});
    let body = {};
    return this.http.post(environment.APIUrl + 'room-categories/import',
      body,
      options).pipe(
      map((response: any) => {
        this.importRooms();
          return response;
        }
      ));
  }

  importRooms(){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});
    let body = {};

    return this.http.post(environment.APIUrl + 'rooms/import',
      body,
      options).pipe(
      map((response: any) => {
          return response;
        }
      ));
  }
}
