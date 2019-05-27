import { Injectable } from '@angular/core';
import {environment} from '../../environments/environment';
import {map, share, timeout} from 'rxjs/operators';
import {HttpClient, HttpHeaders} from '@angular/common/http';

@Injectable({
  providedIn: 'root'
})
export class TimetableService {

  constructor(private http: HttpClient) { }

  getActivitiesGroup(){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});
    return this.http.get(environment.APIUrl + 'activity-categories/',options). //bude sa menit
    // pipe(timeout(20000),
    pipe(
      map((response: any) =>{
          let tmp = [];
          let language = localStorage.getItem('locale')
          for(let item of response){
            if(language === 'en'){
              item['name'] = item['name_en'];
            }
            else{
              item['name'] = item['name_sk'];
            }
          }
          return response;
        }
      ),share());
  }

  getAllEvents(version){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get(environment.APIUrl + 'timetables/'+ version + '/events/',options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  saveEvents(body,version){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.post(environment.APIUrl + 'timetables/'+ version + '/events/',body,options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  updateEvent(body,version){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.post(environment.APIUrl + 'timetables/'+ version + '/events/' + body.id + '/', body, options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  deleteEvent(version: number, id: string) {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.delete(environment.APIUrl + 'timetables/'+ version + '/events/'+id+'/',options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  getAllCollisions(version){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get(environment.APIUrl + 'timetables/'+ version + '/collisions/',options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }


  saveCollision(body, version) {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.post(environment.APIUrl + 'timetables/'+ version + '/collisions/',body,options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  getTimetableVersionLatest(){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({headers: headers});

    return this.http.get(environment.APIUrl + 'timetables/latest/',options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  getLastScheme(){
    return this.http.get(environment.APIUrl + 'version/?status=latest').
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  createSchema(body){
    return this.http.post(environment.APIUrl + 'versions/', body).
    pipe(
      map((response: any) =>{
        localStorage.setItem('active_scheme',body['name']);
        return response;
        }
      ));
  }

  getAllSchemas(){
    return this.http.get(environment.APIUrl + 'versions/').
    pipe(
      map((response: any) =>{
          return response;
        }
      ),share());
  }

  createVersion(body){
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({ headers: headers });
    return this.http.post(environment.APIUrl + 'timetables/',
      body,
      options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }

  finalizeVersion(version) {
    let headers: HttpHeaders = new HttpHeaders();
    headers = headers.append('Timetable-Version', localStorage.getItem('active_scheme'));
    let options = ({ headers: headers });

    let body = {};
    return this.http.post(environment.APIUrl + 'timetables/' + version + '/publish',
      body,
      options).
    pipe(
      map((response: any) =>{
          return response;
        }
      ));
  }
}
