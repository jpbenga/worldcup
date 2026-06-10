import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, map, Observable, of } from 'rxjs';
import {
  AcquisitionSourceStatus,
  DataAcquisitionStatus,
  DataSourceInfo,
  DataSourcesSnapshot,
  DataSourceType,
} from '../models/worldcup.models';

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

interface BackendAcquisitionSourceStatus {
  id: string;
  label: string;
  configured: boolean;
  reachable: boolean;
  usable: boolean;
  worldcup_2026_found: boolean;
  notes: string;
}

interface BackendDataAcquisitionStatus {
  updated_at: string;
  sources: BackendAcquisitionSourceStatus[];
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

  getAcquisitionStatus(): Observable<DataAcquisitionStatus> {
    return this.http.get<BackendDataAcquisitionStatus>('assets/data/data_acquisition_status.json').pipe(
      map((snapshot) => ({
        updatedAt: snapshot.updated_at,
        sources: snapshot.sources.map((source) => this.toAcquisitionSource(source)),
      })),
      catchError(() => of({ updatedAt: '', sources: [] })),
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

  private toAcquisitionSource(source: BackendAcquisitionSourceStatus): AcquisitionSourceStatus {
    return {
      id: source.id,
      label: source.label,
      configured: source.configured,
      reachable: source.reachable,
      usable: source.usable,
      worldcup2026Found: source.worldcup_2026_found,
      notes: source.notes,
    };
  }
}
