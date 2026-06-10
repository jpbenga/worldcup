import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { map, Observable } from 'rxjs';
import { DataSourceInfo, DataSourcesSnapshot, DataSourceType } from '../models/worldcup.models';

interface BackendDataSourceInfo {
  id: string;
  label: string;
  source_type: DataSourceType;
  source_name: string;
  is_real_data: boolean;
  path: string;
  description: string;
}

interface BackendDataSourcesSnapshot {
  version: string;
  updated_at: string;
  sources: BackendDataSourceInfo[];
}

@Injectable({ providedIn: 'root' })
export class DataSourceService {
  private readonly http = inject(HttpClient);

  getSnapshot(): Observable<DataSourcesSnapshot> {
    return this.http.get<BackendDataSourcesSnapshot>('assets/data/data_sources.json').pipe(
      map((snapshot) => ({
        version: snapshot.version,
        updatedAt: snapshot.updated_at,
        sources: snapshot.sources.map((source) => this.toDataSource(source)),
      })),
    );
  }

  private toDataSource(source: BackendDataSourceInfo): DataSourceInfo {
    return {
      id: source.id,
      label: source.label,
      sourceType: source.source_type,
      sourceName: source.source_name,
      isRealData: source.is_real_data,
      path: source.path,
      description: source.description,
    };
  }
}
