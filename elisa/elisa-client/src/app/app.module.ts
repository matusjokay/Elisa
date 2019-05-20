import { BrowserModule } from '@angular/platform-browser';
import { NgModule } from '@angular/core';
import {FormsModule, ReactiveFormsModule} from '@angular/forms';

import { AppComponent } from './app.component';
import { AngularDraggableModule } from 'angular2-draggable';


import { AppRoutingModule } from './app-routing.module';
import { TimetableComponent } from './pages/timetable/timetable/timetable.component';
import { DashboardComponent } from './pages/dashboard/dashboard.component';
import { UserListComponent } from './pages/users/user-list/user-list.component';
import { UserDetailsComponent } from './pages/users/user-details/user-details.component';
import {HTTP_INTERCEPTORS, HttpClientModule} from '@angular/common/http';

import {TokenInterceptor} from './token-interceptor';
import { DepartmentListComponent } from './pages/departments/department-list/department-list.component';
import { NavigationComponent } from './components/navigation/navigation.component';

import {MaterialModule} from './material/material.module';
import { HomeComponent } from './pages/home/home.component';

import { FullCalendarModule } from '@fullcalendar/angular';
import { NavListItemComponent } from './components/nav-list-item/nav-list-item.component';
import { RequirementDetailsComponent } from './pages/requirement/requirement-details/requirement-details.component';
import { RequirementListComponent } from './pages/requirement/requirement-list/requirement-list.component';
import { RequirementFormComponent } from './pages/requirement/requirement-form/requirement-form.component';
import { TimetableUpdateWrapperComponent } from './pages/timetable/timetable-update/timetable-update-wrapper/timetable-update-wrapper.component';
import { TimetableUpdateFormComponent } from './pages/timetable/timetable-update/timetable-update-form/timetable-update-form.component';
import { TimetableUpdateMainComponent } from './pages/timetable/timetable-update/timetable-update-main/timetable-update-main.component';
import { TimetableNewComponent } from './pages/timetable/timetable-new/timetable-new.component';
import { CourseListComponent } from './pages/course/course-list/course-list.component';
import {VersionListComponent} from './pages/version/version-list/version-list.component';
import { RoomsListComponent } from './pages/room/rooms-list/rooms-list.component';
import { EquipmentsListComponent } from './pages/equipment/equipments-list/equipments-list.component';
import {AuthentificationModule} from './authentification/authentification.module';


@NgModule({
  declarations: [
    AppComponent,
    TimetableComponent,
    DashboardComponent,
    UserListComponent,
    UserDetailsComponent,
    DepartmentListComponent,
    NavigationComponent,
    HomeComponent,
    NavListItemComponent,
    RequirementDetailsComponent,
    RequirementListComponent,
    RequirementFormComponent,
    TimetableUpdateWrapperComponent,
    TimetableUpdateFormComponent,
    TimetableUpdateMainComponent,
    TimetableNewComponent,
    CourseListComponent,
    VersionListComponent,
    RoomsListComponent,
    EquipmentsListComponent
  ],
  imports: [
    BrowserModule,
    AuthentificationModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    MaterialModule,
    FullCalendarModule,
    AngularDraggableModule,
  ],
  providers: [{
    provide: HTTP_INTERCEPTORS,
    useClass: TokenInterceptor,
    multi: true
  }],
  bootstrap: [AppComponent],
  entryComponents:[UserDetailsComponent]
})
export class AppModule { }
