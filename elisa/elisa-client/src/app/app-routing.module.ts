import { NgModule } from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { UserListComponent } from './pages/users/user-list/user-list.component';
import {DepartmentListComponent} from './pages/departments/department-list/department-list.component';
import {AuthGuardService} from './services/auth/auth-guard.service';
import {HomeComponent} from './pages/home/home.component';
import {NavigationComponent} from './components/navigation/navigation.component';
import {DashboardComponent} from './pages/dashboard/dashboard.component';
import {RequirementFormComponent} from './pages/requirement/requirement-form/requirement-form.component';
import {
  TimetableUpdateWrapperComponent
} from './pages/timetable/timetable-update/timetable-update-wrapper/timetable-update-wrapper.component';
import {TimetableNewComponent} from './pages/timetable/timetable-new/timetable-new.component';
import {CourseListComponent} from './pages/course/course-list/course-list.component';
import {RoomsListComponent} from './pages/room/rooms-list/rooms-list.component';
import {GroupListComponent} from './pages/group/group-list/group-list.component';
import { LoginFormComponent } from './pages/login/login-form/login-form.component';
import { UserManagerComponent } from './pages/users/user-manager/user-manager.component';
import { VersionSelectComponent } from './pages/version/version-select/version-select.component';
import { MaterialModule } from './material/material.module';
import { RoleManager } from './models/role.model';

const routes: Routes = [
  {
    path: '',
    pathMatch: 'full',
    redirectTo: '/dashboard',
    canActivate: [AuthGuardService],
    data: {roles: RoleManager.ALL}
  },
  {
    path: 'login',
    component: LoginFormComponent
  },
  {
    path: 'version-select',
    component: VersionSelectComponent
  },
  {
    path: '',
    component: NavigationComponent,
    canActivate: [AuthGuardService],
    data: {roles: RoleManager.ALL},
    children: [
      { path: '',
        pathMatch: 'full',
        redirectTo: '/dashboard'
      },
      { path: 'dashboard',
        component: DashboardComponent,
        canActivate: [AuthGuardService],
        // IT FIRST GOES THROUGH THE PARENT AND THEN CHECKS
        // THE CHILDREN WHICH COULD HAVE DIFFERENT ROLE ACCESS
        // AUTH GUARD IS THEREFORE CALLED TWICE
        data: {roles: RoleManager.ALL}
      },
      { path: 'timetable',
        component: HomeComponent,
        canActivate: [AuthGuardService],
        data: {roles: [1]}
      },
      { path: 'new-timetable',
        component: TimetableNewComponent,
        canActivate: [AuthGuardService],
        data: {roles: [3]}
      },
      { path: 'update-timetable',
        component: TimetableUpdateWrapperComponent,
        canActivate: [AuthGuardService],
        data: {roles: [2]}
      },
      { path: 'user-manager',
        component: UserManagerComponent,
        canActivate: [AuthGuardService],
        data: {roles: [1]}
      },
      { path: 'requirement-form',
        component: RequirementFormComponent,
        canActivate: [AuthGuardService],
        data: {roles: [1]}
      },
      { path: 'course-list',
        component: CourseListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [2]}
      },
      { path: 'group-list',
        component: GroupListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [2]}
      },
      { path: 'user-list',
        component: UserListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [2]}
      },
      { path: 'department-list',
        component: DepartmentListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [2]}
      },
      { path: 'room-list',
        component: RoomsListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [2]}
      },
    ]
  },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes),
  MaterialModule],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
