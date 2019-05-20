import { Injectable } from '@angular/core';
import {HttpClient} from '@angular/common/http';
import {Observable} from 'rxjs';
import {environment} from '../../environments/environment';
import {map} from 'rxjs/operators';
import {Room} from '../models/room';

@Injectable({
  providedIn: 'root'
})
export class RoomService {

  constructor(private http: HttpClient) { }

  getAll(): Observable<Room[]>{
    return this.http.get<Room[]>(environment.APIUrl + 'rooms/').
    pipe(
      map((data: Room[]) =>{
          return data;
        }
      ));
  }

  getAllMap(): Observable<Room[]>{
    return this.http.get<Room[]>(environment.APIUrl + 'rooms/').
    pipe(
      map((data:any) =>{
        return data.reduce(function(r, e) {
          r[e.id] = e;
          r[e.id]["events"] = [];
          return r;
        }, {});
        }
      ));
  }
}
