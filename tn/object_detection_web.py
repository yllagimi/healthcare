import cv2
cap = cv2.VideoCapture(0)
with detection_graph.as_default():
    with tf.Session(graph=detection_graph) as sess:
        ret = True
        while (ret):
            ret,image_np = cap.read()
            ops = tf.get_default_graph().get_operations()
            all_tensor_names = {output.name for op in ops for output in op.outputs}
            tensor_dict = {}
            for key in [
                'num_detections', 'detection_boxes', 'detection_scores',
                'detection_classes', 'detection_masks'
            ]:
                tensor_name = key + ':0'
                if tensor_name in all_tensor_names:
                    tensor_dict[key] = tf.get_default_graph().get_tensor_by_name(
                        tensor_name)
                    if 'detection_masks' in tensor_dict:
                        detection_boxes = tf.squeeze(tensor_dict['detection_boxes'], [0])
                        detection_masks = tf.squeeze(tensor_dict['detection_masks'], [0])
                        real_num_detection = tf.cast(tensor_dict['num_detections'][0], tf.int32)
                        detection_boxes = tf.slice(detection_boxes, [0, 0], [real_num_detection, -1])
                        detection_masks = tf.slice(detection_masks, [0, 0, 0], [real_num_detection, -1, -1])
                        detection_masks_reframed = utils_ops.reframe_box_masks_to_image_masks(
                            detection_masks, detection_boxes, image.shape[0], image.shape[1])
                        detection_masks_reframed = tf.cast(
                            tf.greater(detection_masks_reframed, 0.5), tf.uint8)
                        tensor_dict['detection_masks'] = tf.expand_dims(
                            detection_masks_reframed, 0)
                        image_tensor = tf.get_default_graph().get_tensor_by_name('image_tensor:0')
                        image_np_expanded = np.expand_dims(image_np, axis=0)
                        output_dict = run_inference_for_single_image(image_np, detection_graph)
                        vis_util.visualize_boxes_and_labels_on_image_array(
                            image_np,
                            output_dict['detection_boxes'],
                            output_dict['detection_classes'],
                            output_dict['detection_scores'],
                            category_index,
                            instance_masks=output_dict.get('detection_masks'),
                            use_normalized_coordinates=True,
                            line_thickness=7)
                        output_dict = sess.run(tensor_dict,
                                               feed_dict={image_tensor: np.expand_dims(image, 0)})
                        output_dict['num_detections'] = int(output_dict['num_detections'][0])
                        output_dict['detection_classes'] = output_dict[
                            'detection_classes'][0].astype(np.uint8)
                        output_dict['detection_boxes'] = output_dict['detection_boxes'][0]
                        output_dict['detection_scores'] = output_dict['detection_scores'][0]
#                         if 'detection_masks' in output_dict:
#                             output_dict['detection_masks'] = output_dict['detection_masks'][0]
#                             return output_dict
                        cv2.imshow('image',cv2.resize(image_np,(1200,960)))
                        if cv2.waitKey(25) & 0xFF == ord('Q'):
                            break
                            cv2.destroyAllWindows()
                            cap.release()