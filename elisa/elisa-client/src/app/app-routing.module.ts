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
import { NotFoundComponent } from './common/not-found/not-found.component';
import { RequirementListComponent } from './pages/requirement/requirement-list/requirement-list.component';

const routes: Routes = [
  {
    path: 'login',
    component: LoginFormComponent
  },
  {
    path: 'version-select',
    component: VersionSelectComponent,
    canActivate: [AuthGuardService],
    data: {roles: RoleManager.ALL},
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
        // canActivate: [AuthGuardService],
        // data: {roles: RoleManager.ALL}
      },
      { path: 'timetable',
        component: HomeComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
        ]}
      },
      { path: 'new-timetable',
        component: TimetableNewComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
        ]}
      },
      { path: 'update-timetable',
        component: TimetableUpdateWrapperComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
        ]}
      },
      { path: 'user-manager',
        component: UserManagerComponent,
        canActivate: [AuthGuardService],
        data: {roles: RoleManager.ALL}
      },
      { path: 'requirement-form',
        component: RequirementFormComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
          RoleManager.TEACHER
        ]}
      },
      { path: 'requirement-list',
        component: RequirementListComponent,
        canActivate: [AuthGuardService],
        data: {roles: RoleManager.ALL}
      },
      { path: 'course-list',
        component: CourseListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
          RoleManager.TEACHER
        ]}
      },
      { path: 'group-list',
        component: GroupListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
          RoleManager.TEACHER
        ]}
      },
      { path: 'user-list',
        component: UserListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
          RoleManager.TEACHER
        ]}
      },
      { path: 'department-list',
        component: DepartmentListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
          RoleManager.TEACHER
        ]}
      },
      { path: 'room-list',
        component: RoomsListComponent,
        canActivate: [AuthGuardService],
        data: {roles: [
          RoleManager.MAIN_TIMETABLE_CREATOR,
          RoleManager.LOCAL_TIMETABLE_CREATOR,
          RoleManager.TEACHER
        ]}
      },
    ]
  },
  {
    path: '**',
    component: NotFoundComponent
  }
];

@NgModule({
  imports: [ RouterModule.forRoot(routes),
  MaterialModule],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
