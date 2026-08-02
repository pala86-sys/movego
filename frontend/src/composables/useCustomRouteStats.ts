/** 自訂路線的站數／轉乘／預估時間統計，即時依目前捷運站點資料算出來，不存在自訂路線本身。 */
import type { CustomRouteLeg, MetroLine } from "@/types";

// 跟後端 metro_service.py 的 MINUTES_PER_STOP / MINUTES_PER_TRANSFER 保持一致，
// 讓自訂路線跟系統路線的時間估算邏輯相同，數字才有可比性。
const MINUTES_PER_STOP = 2;
const MINUTES_PER_TRANSFER = 4;

export function legStopCount(leg: CustomRouteLeg, lines: MetroLine[]): number {
  const line = lines.find((l) => l.id === leg.lineId);
  if (!line) return 0;
  const names = line.stations.map((s) => s.name);
  const from = names.indexOf(leg.from);
  const to = names.indexOf(leg.to);
  if (from === -1 || to === -1) return 0;
  return Math.abs(to - from);
}

export interface CustomRouteStats {
  totalStopCount: number;
  transferCount: number;
  estimatedMinutes: number;
}

export function computeCustomRouteStats(legs: CustomRouteLeg[], lines: MetroLine[]): CustomRouteStats {
  const totalStopCount = legs.reduce((sum, leg) => sum + legStopCount(leg, lines), 0);
  const transferCount = Math.max(legs.length - 1, 0);
  const estimatedMinutes = totalStopCount * MINUTES_PER_STOP + transferCount * MINUTES_PER_TRANSFER;
  return { totalStopCount, transferCount, estimatedMinutes };
}
