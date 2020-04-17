import { environment } from './../../environments/environment';
import { BaseService } from 'src/app/services/base-service.service';
import { HttpClient } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Period } from '../models/period.model';
import { Observable } from 'rxjs';
import { shareReplay } from 'rxjs/operators';

@Injectable({
  providedIn: 'root'
})
export class PeriodService {

  private cachePeriodList$: Observable<Array<Period>>;

  constructor(private http: HttpClient,
    private baseService: BaseService) { }

  getAllPeriods(): Observable<Period[]> {
    const httpOptions = this.baseService.getAuthHeaderOnly();
    return this.http.get<Period[]>(`${environment.APIUrl}periods/`,
      { headers: httpOptions });
  }

  getCurrentSelectedPeriods() {
    if (!this.cachePeriodList$) {
      this.cachePeriodList$ = this.requestPeriods().pipe(
        shareReplay(1)
      );
    }

    return this.cachePeriodList$;
  }

  private requestPeriods(): Observable<Period[]> {
    const httpOptions = this.baseService.getSchemaHeader();
    return this.http.get<Period[]>(environment.APIUrl + 'periods/current/', { headers: httpOptions });
  }

}
