SELECT schedule_program_view_query.id,
    schedule_program_view_query.name,
    schedule_program_view_query.start,
    schedule_program_view_query._end,
    schedule_program_view_query.series_id,
    schedule_program_view_query.station_id,
    schedule_program_view_query.color
   FROM ( SELECT radio_program.name,
            radio_scheduledprogram.id,
            radio_scheduledprogram.start,
            radio_scheduledprogram."end" AS _end,
            radio_program.program_type_id,
            radio_scheduledprogram.series_id,
            radio_scheduledprogram.station_id,
                CASE
                    WHEN radio_scheduledprogram.status = 0 THEN 'red'::text
                    WHEN radio_scheduledprogram.status = 1 THEN 'green'::text
                    WHEN radio_scheduledprogram.status = 2 THEN 'grey'::text
                    WHEN radio_program.program_type_id = 2 THEN 'blue'::text
                    ELSE 'yellow'::text
                END AS color
           FROM radio_scheduledprogram
             JOIN radio_program ON radio_scheduledprogram.program_id = radio_program.id
          WHERE radio_scheduledprogram.deleted IS NOT TRUE AND radio_scheduledprogram."end" < now() AND radio_scheduledprogram.deleted <> true
        UNION
         SELECT scheduled_program_query.name,
            scheduled_program_query.id,
            scheduled_program_query.start,
            scheduled_program_query._end,
            scheduled_program_query.program_type_id,
            scheduled_program_query.series_id,
            scheduled_program_query.station_id,
                CASE
                    WHEN max(scheduled_program_query.count) > 0 THEN
                    CASE
                        WHEN scheduled_program_query.program_type_id = 2 THEN 'blue'::text
                        ELSE 'yellow'::text
                    END
                    ELSE 'grey'::text
                END AS color
           FROM ( SELECT DISTINCT radio_program.name,
                    radio_scheduledprogram.id,
                    radio_scheduledprogram.start,
                    radio_scheduledprogram."end" AS _end,
                    radio_program.program_type_id,
                    radio_scheduledprogram.series_id,
                    radio_scheduledprogram.station_id,
                    count(radio_scheduledprogram.id) FILTER (WHERE content_communitycontent.valid_until > radio_scheduledprogram.start) AS count
                   FROM radio_scheduledprogram
                     JOIN radio_program ON radio_scheduledprogram.program_id = radio_program.id
                     JOIN content_communitycontent ON radio_program.structure ~~* (('%'::text || concat('"type":"Community", "category_id":"', content_communitycontent.type_code)) || '%'::text)
                  WHERE radio_scheduledprogram.deleted <> true AND radio_scheduledprogram."end" >= now()
                  GROUP BY radio_scheduledprogram.id, radio_program.program_type_id, radio_program.name, content_communitycontent.type_code, content_communitycontent.station_id, content_communitycontent.valid_until
                UNION
                 SELECT radio_program.name,
                    radio_scheduledprogram.id,
                    radio_scheduledprogram.start,
                    radio_scheduledprogram."end" AS _end,
                    radio_program.program_type_id,
                    radio_scheduledprogram.series_id,
                    radio_scheduledprogram.station_id,
                    count(content_podcast.id) FILTER (WHERE content_podcast.ok_to_play = true) AS count
                   FROM radio_scheduledprogram
                     JOIN radio_program ON radio_scheduledprogram.program_id = radio_program.id
                     JOIN content_podcast ON radio_program.structure ~~* (('%'::text || concat('"type":"Podcast","track_id":', content_podcast.id)) || '%'::text)
                  WHERE radio_scheduledprogram."end" >= now() AND radio_scheduledprogram.deleted <> true AND radio_program.program_type_id = 1
                  GROUP BY radio_scheduledprogram.id, radio_program.name, radio_program.program_type_id
                UNION
                 SELECT radio_program.name,
                    radio_scheduledprogram.id,
                    radio_scheduledprogram.start,
                    radio_scheduledprogram."end" AS _end,
                    radio_program.program_type_id,
                    radio_scheduledprogram.series_id,
                    radio_scheduledprogram.station_id,
                    count(content_track.id) FILTER (WHERE content_track.deleted <> true) AS count
                   FROM radio_scheduledprogram
                     JOIN radio_program ON radio_scheduledprogram.program_id = radio_program.id
                     JOIN content_track ON radio_program.structure ~~* (('%'::text || concat('"type":"Advertisements","track_id":', content_track.id)) || '%'::text)
                  WHERE radio_scheduledprogram."end" >= now() AND radio_scheduledprogram.deleted <> true AND radio_program.program_type_id = 1
                  GROUP BY radio_scheduledprogram.id, radio_program.name, radio_program.program_type_id
                UNION
                 SELECT radio_program.name,
                    radio_scheduledprogram.id,
                    radio_scheduledprogram.start,
                    radio_scheduledprogram."end" AS _end,
                    radio_program.program_type_id,
                    radio_scheduledprogram.series_id,
                    radio_scheduledprogram.station_id,
                    count(content_track.id) FILTER (WHERE content_track.deleted <> true) AS count
                   FROM radio_scheduledprogram
                     JOIN radio_program ON radio_scheduledprogram.program_id = radio_program.id
                     JOIN content_track ON radio_program.structure ~~* (('%'::text || concat('"type":"Media","track_id":', content_track.id)) || '%'::text)
                  WHERE radio_scheduledprogram."end" >= now() AND radio_scheduledprogram.deleted <> true AND radio_program.program_type_id = 1
                  GROUP BY radio_scheduledprogram.id, radio_program.name, radio_program.program_type_id
                UNION
                 SELECT radio_program.name,
                    radio_scheduledprogram.id,
                    radio_scheduledprogram.start,
                    radio_scheduledprogram."end" AS _end,
                    radio_program.program_type_id,
                    radio_scheduledprogram.series_id,
                    radio_scheduledprogram.station_id,
                    0 AS count
                   FROM radio_scheduledprogram
                     JOIN radio_program ON radio_scheduledprogram.program_id = radio_program.id
                  WHERE radio_scheduledprogram."end" >= now() AND radio_scheduledprogram.deleted <> true AND radio_program.program_type_id = 1 AND (radio_program.structure = '{}'::text OR radio_program.structure = ''::text OR radio_program.structure IS NULL)
                  GROUP BY radio_scheduledprogram.id, radio_program.name, radio_program.program_type_id
                UNION
                 SELECT radio_program.name,
                    radio_scheduledprogram.id,
                    radio_scheduledprogram.start,
                    radio_scheduledprogram."end" AS _end,
                    radio_program.program_type_id,
                    radio_scheduledprogram.series_id,
                    radio_scheduledprogram.station_id,
                    1 AS count
                   FROM radio_scheduledprogram
                     JOIN radio_program ON radio_scheduledprogram.program_id = radio_program.id
                  WHERE radio_scheduledprogram."end" >= now() AND radio_scheduledprogram.deleted <> true AND radio_program.program_type_id = 2
                  GROUP BY radio_scheduledprogram.id, radio_program.name, radio_program.program_type_id
                UNION
                 SELECT radio_program.name,
                    radio_scheduledprogram.id,
                    radio_scheduledprogram.start,
                    radio_scheduledprogram."end" AS _end,
                    radio_program.program_type_id,
                    radio_scheduledprogram.series_id,
                    radio_scheduledprogram.station_id,
                    count(radio_person.id) FILTER (WHERE radio_person.deleted <> true) AS count
                   FROM radio_scheduledprogram
                     JOIN radio_program ON radio_scheduledprogram.program_id = radio_program.id
                     JOIN radio_person ON radio_program.structure ~~* (('%'::text || concat('"type":"Outcall","host_id":', radio_person.id)) || '%'::text)
                  WHERE radio_scheduledprogram."end" >= now() AND radio_scheduledprogram.deleted <> true AND radio_program.program_type_id = 1
                  GROUP BY radio_scheduledprogram.id, radio_program.name, radio_program.program_type_id
          ORDER BY 3) scheduled_program_query
          GROUP BY scheduled_program_query.id, scheduled_program_query.start, scheduled_program_query._end, scheduled_program_query.name, scheduled_program_query.program_type_id, scheduled_program_query.series_id, scheduled_program_query.station_id) schedule_program_view_query
  ORDER BY schedule_program_view_query.start;