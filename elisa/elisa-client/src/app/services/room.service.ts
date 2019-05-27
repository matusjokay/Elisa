import { Injectable } from '@angular/core';
import {HttpClient, HttpHeaders} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map, share} from 'rxjs/operators';
import {Room} from '../models/room';

@Injectable({
  providedIn: 'root'
})
export class RoomService {

  constructor(private http: HttpClient) { }

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
