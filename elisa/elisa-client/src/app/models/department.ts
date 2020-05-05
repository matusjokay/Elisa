export class Department {
  id?: number;
  name: string;
  abbr: string;
  parent?: number;
  public constructor(init?: Partial<Department>) {
    Object.assign(this, init);
  }
}

export class DepartmentNode {
  id?: number;
  name: string;
  abbr: string;
  parent?: number;
  children?: DepartmentNode[];
}
