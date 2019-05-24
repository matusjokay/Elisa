import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { UserListComponent } from './pages/users/user-list/user-list.component';
import {DepartmentListComponent} from './pages/departments/department-list/department-list.component';
import {AuthGuardService} from './services/auth/auth-guard.service';
import {HomeComponent} from './pages/home/home.component';
import {NavigationComponent} from './components/navigation/navigation.component';
import {DashboardComponent} from './pages/dashboard/dashboard.component';
import {RequirementFormComponent} from './pages/requirement/requirement-form/requirement-form.component';
import {TimetableUpdateWrapperComponent} from './pages/timetable/timetable-update/timetable-update-wrapper/timetable-update-wrapper.component';
import {TimetableNewComponent} from './pages/timetable/timetable-new/timetable-new.component';
import {CourseListComponent} from './pages/course/course-list/course-list.component';
import {VersionListComponent} from './pages/version/version-list/version-list.component';
import {RoomsListComponent} from './pages/room/rooms-list/rooms-list.component';
import {GroupListComponent} from './pages/group/group-list/group-list.component';

const routes: Routes = [
  { path: '', component: HomeComponent },
  { path: 'login', loadChildren: './authentification/authentification.module#AuthentificationModule'},
  { path: 'admin', component: NavigationComponent, canActivate:[AuthGuardService], data:{role:1}, children:[
    { path: '', pathMatch: 'full', redirectTo: '/admin/(adminView:dashboard)'},
    { path: 'dashboard', component: DashboardComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:1}},
    { path: 'timetable', component: HomeComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:1}},
    { path: 'new-timetable', component: TimetableNewComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:3}},
    { path: 'update-timetable', component: TimetableUpdateWrapperComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:2}},
    { path: 'requirement-form', component: RequirementFormComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:1}},
    { path: 'version-list', component: VersionListComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:2}},
    { path: 'course-list', component: CourseListComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:2}},
    { path: 'group-list', component: GroupListComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:2}},
    { path: 'user-list', component: UserListComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:2}},
    { path: 'department-list', component: DepartmentListComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:2}},
    { path: 'room-list', component: RoomsListComponent, outlet: 'adminView', canActivate:[AuthGuardService], data:{role:2}},
    ]},
];

@NgModule({
  imports: [ RouterModule.forRoot(routes)],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
