import { HttpClient } from '@angular/common/http';
import { inject, Injectable } from '@angular/core';
import { catchError, map, Observable, of } from 'rxjs';
import {
  AcquisitionSourceStatus,
  DataAcquisitionStatus,
  DataSourceInfo,
  DataSourcesSnapshot,
  DataSourceType,
  TeamMappingStatus,
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

interface BackendTeamMappingStatus {
  updated_at: string;
  status: TeamMappingStatus['status'];
  api_football_teams_count: number;
  elo_teams_count: number;
  mapped_count: number;
  auto_validated_count: number;
  needs_review_count: number;
  unmapped_api_count: number;
  coverage_percent: number;
  elo_connected_to_prediction_engine: boolean;
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

  getTeamMappingStatus(): Observable<TeamMappingStatus | null> {
    return this.http.get<BackendTeamMappingStatus>('assets/data/team_mapping_status.json').pipe(
      map((snapshot) => ({
        updatedAt: snapshot.updated_at,
        status: snapshot.status,
        apiFootballTotal: snapshot.api_football_teams_count,
        eloTotal: snapshot.elo_teams_count,
        matched: snapshot.mapped_count,
        autoValidated: snapshot.auto_validated_count,
        needsReview: snapshot.needs_review_count,
        unmappedApiFootball: snapshot.unmapped_api_count,
        coveragePercent: snapshot.coverage_percent,
        eloConnectedToPredictionEngine: snapshot.elo_connected_to_prediction_engine,
      })),
      catchError(() => of(null)),
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
