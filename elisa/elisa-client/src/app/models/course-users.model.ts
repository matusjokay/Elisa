export interface CourseUser {
    idRow?: number;
    userId: number;
    userFullname: string;
    rolesAmount?: number;
    isOpened?: boolean;
    roles?: CourseUserRole[];
}

export interface CourseUserRole {
    idRow: number;
    roleId: number;
}

export interface CourseRole {
    id: number;
    name?: string;
}
