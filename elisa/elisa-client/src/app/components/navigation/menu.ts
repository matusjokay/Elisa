import {NavItem} from './nav-item';
import { RoleManager } from 'src/app/models/role.model';

export const navItems: NavItem[] = [
  {
    displayName: 'Dashboard',
    iconName: 'home',
    route: ['/dashboard'],
    i18n: '@@dashboard',
    forRoles: RoleManager.ID_ALL
  },
  {
    displayName: 'Timetable',
    iconName: 'calendar_today',
    route: ['/timetable'],
    i18n: '@@timetable',
    forRoles: [
      RoleManager.MAIN_TIMETABLE_CREATOR.id,
      RoleManager.LOCAL_TIMETABLE_CREATOR.id
    ],
  },
  {
    displayName: 'Timetable creation',
    iconName: 'add',
    i18n: '@@timetable-creation',
    forRoles: [
      RoleManager.MAIN_TIMETABLE_CREATOR.id,
      RoleManager.LOCAL_TIMETABLE_CREATOR.id
    ],
    children: [
      {
        displayName: 'Update timetable',
        route: ['/update-timetable'],
        i18n: '@@timetable-update'
      },
      {
        displayName: 'New timetable',
        route: ['/new-timetable'],
        i18n: '@@timetable-new'
      },
    ]
  },
  {
    displayName: 'Requirement',
    iconName: 'note_add',
    route: ['/requirement-form'],
    i18n: '@@Requirement',
    forRoles: RoleManager.ID_ALL
  },
  {
    displayName: 'User Manager',
    iconName: 'people',
    route: ['/user-manager'],
    i18n: '@@Manager',
    forRoles: [
      RoleManager.MAIN_TIMETABLE_CREATOR.id,
      RoleManager.LOCAL_TIMETABLE_CREATOR.id,
      RoleManager.TEACHER.id
    ]
  },
  {
    displayName: 'Data',
    iconName: 'storage',
    i18n: '@@data',
    forRoles: [
      RoleManager.MAIN_TIMETABLE_CREATOR.id,
      RoleManager.LOCAL_TIMETABLE_CREATOR.id
    ],
    children: [
      {
        displayName: 'Courses',
        route: ['/course-list'],
        i18n: '@@Courses'
      },
      {
        displayName: 'Users',
        route: ['/user-list'],
        i18n: '@@users'
      },
      {
        displayName: 'Departments',
        route: ['/department-list'],
        i18n: '@@departments'
      },
      {
        displayName: 'Groups',
        route: ['/group-list'],
        i18n: '@@Requirements'
      },
      {
        displayName: 'Rooms',
        route: ['/room-list'],
        i18n: '@@rooms'
      }
    ]
  },
];
