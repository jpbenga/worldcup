import { AsyncPipe, DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { combineLatest } from 'rxjs';
import { DataSourceInfo, DataSourcesSnapshot, Match, MatchPrediction } from '../../models/worldcup.models';
import { BacktestingService } from '../../services/backtesting.service';
import { MatchService } from '../../services/match.service';
import { PredictionService } from '../../services/prediction.service';
import { MatchDetailComponent } from '../../components/match-detail/match-detail.component';
import { MatchListComponent } from '../../components/match-list/match-list.component';
import { PredictionHistoryComponent } from '../../components/prediction-history/prediction-history.component';
import { ResponsibleNoticeComponent } from '../../components/responsible-notice/responsible-notice.component';
import { DataSourceBadgeComponent } from '../../components/data-source-badge/data-source-badge.component';
import { DataSourceService } from '../../services/data-source.service';

@Component({
  selector: 'app-home',
  imports: [
    AsyncPipe,
    DatePipe,
    DataSourceBadgeComponent,
    MatchDetailComponent,
    MatchListComponent,
    PredictionHistoryComponent,
    ResponsibleNoticeComponent,
  ],
  templateUrl: './home.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent {
  private readonly matchService = inject(MatchService);
  private readonly predictionService = inject(PredictionService);
  private readonly backtestingService = inject(BacktestingService);
  private readonly dataSourceService = inject(DataSourceService);

  readonly selectedPrediction = signal<MatchPrediction | null>(null);
  readonly viewModel$ = combineLatest({
    matches: this.matchService.getMatches(),
    predictions: this.predictionService.getPredictions(),
    backtests: this.backtestingService.getResults(),
    dataSources: this.dataSourceService.getSnapshot(),
    acquisitionStatus: this.dataSourceService.getAcquisitionStatus(),
    teamMappingStatus: this.dataSourceService.getTeamMappingStatus(),
  });

  selectPrediction(prediction: MatchPrediction): void {
    this.selectedPrediction.set(prediction);
    setTimeout(() => document.querySelector('#match-detail')?.scrollIntoView({ behavior: 'smooth' }));
  }

  matchFor(matches: Match[], matchId: string): Match | undefined {
    return matches.find((match) => match.id === matchId);
  }

  primarySource(snapshot: DataSourcesSnapshot): DataSourceInfo | undefined {
    return snapshot.sources.find((source) => source.id === 'sample_matches');
  }
}
