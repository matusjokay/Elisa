import { RoleAuth } from 'src/app/models/role.model';
export interface NavItem {
  displayName: string;
  iconName?: string;
  route?: any;
  i18n: string;
  children?: NavItem[];
  forRoles?: number[];
}
