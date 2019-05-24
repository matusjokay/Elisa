import {NavItem} from './nav-item';

export const navItems: NavItem[] = [
  {
    displayName: 'Dashboard',
    iconName: 'home',
    route: ['/admin',{outlets:{adminView:'dashboard'}}],
    i18n:"@@dashboard"
  },
  {
    displayName: 'Timetable',
    iconName: 'calendar_today',
    route: [{outlets:{adminView:['timetable']}}],
    i18n:"@@timetable"
  },
  {
    displayName: 'Timetable creation',
    iconName: 'add',
    i18n:"@@timetable-creation",
    children:[
      {
        displayName: 'Update timetable',
        route: [{outlets:{adminView:['update-timetable']}}],
        i18n:"@@timetable-update"
      },
      {
        displayName: 'New timetable',
        route: [{outlets:{adminView:['new-timetable']}}],
        i18n:"@@timetable-new"
      },
    ]
  },
  {
    displayName: 'Requirement',
    iconName: 'note_add',
    route: [{outlets:{adminView:['requirement-form']}}],
    i18n:"@@Requirement"
  },
  {
    displayName: 'Data',
    iconName: 'storage',
    i18n:"@@data",
    children:[
      // {
      //   displayName: 'Versions',
      //   route: [{outlets:{adminView:['version-list']}}],
      //   i18n:"@@Versions"
      // },
      {
        displayName: 'Courses',
        route: [{outlets:{adminView:['course-list']}}],
        i18n:"@@Courses"
      },
      {
        displayName: 'Users',
        route: [{outlets:{adminView:['user-list']}}],
        i18n:"@@users"
      },
      {
        displayName: 'Departments',
        route: [{outlets:{adminView:['department-list']}}],
        i18n:"@@departments"
      },
      {
        displayName: 'Groups',
        route: [{outlets:{adminView:['group-list']}}],
        i18n:"@@Requirements"
      },
      {
        displayName: 'Rooms',
        route: [{outlets:{adminView:['room-list']}}],
        i18n:"@@rooms"
      },
      // {
      //   displayName: 'Equipments',
      //   route: [{outlets:{adminView:['equipment-list']}}],
      //   i18n:"@@equipments"
      // },
      {
        displayName: 'Requirements',
        route: [{outlets:{adminView:['Requirement-list']}}],
        i18n:"@@Requirements"
      },
    ]
  },
];
