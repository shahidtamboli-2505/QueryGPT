export type Row = Record<string, string | number | boolean | null>;
export type QueryResult = {question:string;sql:string|null;columns:string[];rows:Row[];result_count:number;execution_ms:number;status:string;mode:string;error?:string|null};
export type TableInfo = {name:string;row_count:number;columns?:{name:string;type:string;primary_key:boolean;notnull:boolean}[];foreign_keys?:{from_column:string;to_table:string;to_column:string}[]};
export type HistoryItem = {id:number;question:string;generated_sql:string|null;status:string;mode:string;result_count:number;execution_ms:number|null;error:string|null;created_at:string};
