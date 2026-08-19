<?php
/**
 * Plugin Name: AI Publisher SEO Meta
 * Install as wp-content/mu-plugins/ai-publisher-seo-meta.php. MU plugins auto-load; no activation needed.
 */
add_action('init', function () {
  foreach (array('_yoast_wpseo_focuskw','_yoast_wpseo_metadesc','rank_math_focus_keyword','rank_math_description') as $key) {
    register_post_meta('post', $key, array('type'=>'string','single'=>true,'show_in_rest'=>true,
      'auth_callback'=>function($allowed, $meta_key, $post_id) { return current_user_can('edit_post', $post_id); }));
  }
});
add_action('rest_api_init', function () {
  register_rest_route('ai-publisher/v1', '/seo-meta/(?P<post_id>\\d+)', array(
    'methods'=>'POST',
    'permission_callback'=>function($request) { return current_user_can('edit_post', (int)$request['post_id']); },
    'callback'=>function($request) {
      $post_id=(int)$request['post_id'];
      foreach (array('_yoast_wpseo_focuskw','_yoast_wpseo_metadesc','rank_math_focus_keyword','rank_math_description') as $key)
        if ($request->has_param($key)) update_post_meta($post_id, $key, sanitize_text_field($request->get_param($key)));
      return new WP_REST_Response(array('post_id'=>$post_id,'updated'=>true), 200);
    }
  ));
});
