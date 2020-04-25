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
import {HTTP_INTERCEPTORS, HttpClientModule, HttpClientXsrfModule} from '@angular/common/http';

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
import {
  TimetableUpdateWrapperComponent
} from './pages/timetable/timetable-update/timetable-update-wrapper/timetable-update-wrapper.component';
import { TimetableUpdateFormComponent } from './pages/timetable/timetable-update/timetable-update-form/timetable-update-form.component';
import { TimetableUpdateMainComponent } from './pages/timetable/timetable-update/timetable-update-main/timetable-update-main.component';
import { TimetableNewComponent } from './pages/timetable/timetable-new/timetable-new.component';
import { CourseListComponent } from './pages/course/course-list/course-list.component';
import { RoomsListComponent } from './pages/room/rooms-list/rooms-list.component';
import { EquipmentsListComponent } from './pages/equipment/equipments-list/equipments-list.component';
import { CollisionCardComponent } from './components/collision-card/collision-card.component';
import { CollisionDetailComponent } from './components/collision-detail/collision-detail.component';
import { EventDetailComponent } from './components/event-detail/event-detail.component';
import { CourseDetailsComponent } from './pages/course/course-details/course-details.component';
import { GroupDetailsComponent } from './pages/group/group-details/group-details.component';
import { GroupListComponent } from './pages/group/group-list/group-list.component';
import { RoomDetailsComponent } from './pages/room/room-details/room-details.component';
import { ErrorStateMatcher, ShowOnDirtyErrorStateMatcher } from '@angular/material/core';
import { SnackbarComponent } from './common/snackbar/snackbar.component';
import { SpinnerComponent } from './common/spinner/spinner.component';
import { LoginFormComponent } from './pages/login/login-form/login-form.component';
import { UserManagerComponent } from './pages/users/user-manager/user-manager.component';
import { VersionSelectComponent } from './pages/version/version-select/version-select.component';
import { UserRoleDetailComponent } from './pages/users/user-manager/user-role-detail/user-role-detail.component';
import { VersionImportComponent } from './pages/version/version-import/version-import.component';
import { ParsePeriodsPipe } from './pipes/parse-periods.pipe';
import { CourseTeacherComponent } from './pages/course/course-teacher/course-teacher.component';
import { CourseRolesPipe } from './pipes/course-roles.pipe';
import { CourseRolesAvailablePipe } from './pipes/course-roles-available.pipe';
import { UserSearchComponent } from './common/user-search/user-search.component';
import { ConfirmDialogComponent } from './common/confirm-dialog/confirm-dialog.component';
import { NotFoundComponent } from './common/not-found/not-found.component';


@NgModule({
  declarations: [
    AppComponent,
    LoginFormComponent,
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
    RoomsListComponent,
    EquipmentsListComponent,
    CollisionCardComponent,
    CollisionDetailComponent,
    EventDetailComponent,
    CourseDetailsComponent,
    GroupDetailsComponent,
    GroupListComponent,
    RoomDetailsComponent,
    SnackbarComponent,
    SpinnerComponent,
    UserManagerComponent,
    VersionSelectComponent,
    UserRoleDetailComponent,
    VersionImportComponent,
    ParsePeriodsPipe,
    CourseTeacherComponent,
    CourseRolesPipe,
    CourseRolesAvailablePipe,
    UserSearchComponent,
    ConfirmDialogComponent,
    NotFoundComponent
  ],
  imports: [
    BrowserModule,
    MaterialModule,
    AppRoutingModule,
    FormsModule,
    ReactiveFormsModule,
    HttpClientModule,
    HttpClientXsrfModule.withOptions(
      { headerName: 'Authorization' }
    ),
    FullCalendarModule,
    AngularDraggableModule,
  ],
  providers: [{
    provide: HTTP_INTERCEPTORS,
    useClass: TokenInterceptor,
    multi: true
  },
  {provide: ErrorStateMatcher, useClass: ShowOnDirtyErrorStateMatcher},
  SnackbarComponent
  ],
  bootstrap: [AppComponent],
  entryComponents: [
    UserDetailsComponent,
    CourseDetailsComponent,
    RoomDetailsComponent,
    GroupDetailsComponent,
    CollisionDetailComponent,
    EventDetailComponent
  ]
})
export class AppModule { }
