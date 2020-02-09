// export class Department {
//   public id: number;
//   public name: string;
//   public abbr: string;
//   public parent: number;
//   public children: any[];
//   constructor(
//     id: number,
//     name: string,
//     abbr: string,
//     parent: number,
//   ) {
//     this.id=id;
//     this.name=name;
//     this.abbr=abbr;
//     this.parent=parent;
//   }
// }

export class Department {
  id?: number;
  name: string;
  abbr: string;
  parent?: number;
  public constructor(init?: Partial<Department>) {
    Object.assign(this, init);
  }
}
