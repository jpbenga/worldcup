import { AsyncPipe, DatePipe } from '@angular/common';
import { ChangeDetectionStrategy, Component, inject, signal } from '@angular/core';
import { RouterLink } from '@angular/router';
import { combineLatest } from 'rxjs';
import { DataSourceInfo, DataSourcesSnapshot, MatchPrediction, MatchState, ModelComparison } from '../../models/worldcup.models';
import { BacktestingService } from '../../services/backtesting.service';
import { MatchService } from '../../services/match.service';
import { PredictionService } from '../../services/prediction.service';
import { PredictionHistoryComponent } from '../../components/prediction-history/prediction-history.component';
import { ResponsibleNoticeComponent } from '../../components/responsible-notice/responsible-notice.component';
import { DataSourceBadgeComponent } from '../../components/data-source-badge/data-source-badge.component';
import { DataSourceService } from '../../services/data-source.service';
import { ModelComparisonService } from '../../services/model-comparison.service';
import { WorldCupService } from '../../services/worldcup.service';
import { GroupTabsComponent } from '../../components/group-tabs/group-tabs.component';
import { MatchModalComponent } from '../../components/match-modal/match-modal.component';

@Component({
  selector: 'app-home',
  imports: [
    AsyncPipe,
    DatePipe,
    DataSourceBadgeComponent,
    GroupTabsComponent,
    MatchModalComponent,
    PredictionHistoryComponent,
    ResponsibleNoticeComponent,
    RouterLink,
  ],
  templateUrl: './home.component.html',
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class HomeComponent {
  private readonly matchService = inject(MatchService);
  private readonly predictionService = inject(PredictionService);
  private readonly backtestingService = inject(BacktestingService);
  private readonly dataSourceService = inject(DataSourceService);
  private readonly modelComparisonService = inject(ModelComparisonService);
  private readonly worldCupService = inject(WorldCupService);

  readonly selectedMatchId = signal<string | null>(null);
  readonly viewModel$ = combineLatest({
    matches: this.matchService.getMatches(),
    predictions: this.predictionService.getPredictions(),
    eloPredictions: this.predictionService.getEloPredictions(),
    backtests: this.backtestingService.getResults(),
    dataSources: this.dataSourceService.getSnapshot(),
    acquisitionStatus: this.dataSourceService.getAcquisitionStatus(),
    teamMappingStatus: this.dataSourceService.getTeamMappingStatus(),
    modelComparisons: this.modelComparisonService.getComparisons(),
    groups: this.worldCupService.getGroups(),
    groupStrengths: this.worldCupService.getStrengths(),
    matchStates: this.worldCupService.getMatchStates(),
    liveStandings: this.worldCupService.getLiveGroupStandings(),
  });

  predictionFor(predictions: MatchPrediction[], matchId: string): MatchPrediction | undefined {
    return predictions.find((prediction) => prediction.matchId === matchId);
  }

  comparisonFor(comparisons: ModelComparison[], matchId: string): ModelComparison | undefined {
    return comparisons.find((comparison) => comparison.matchId === matchId);
  }

  matchStateFor(states: MatchState[], matchId: string): MatchState | undefined {
    return states.find((state) => state.matchId === matchId);
  }

  primarySource(snapshot: DataSourcesSnapshot): DataSourceInfo | undefined {
    return snapshot.sources.find((source) => source.id === 'active_matches');
  }
}
